import logging
import multiprocessing
import ast

import json # Moved to module-level import
logger = logging.getLogger(__name__)

TIMEOUT_SECONDS: float = 10.0

def _safe_exec_worker(code, globals_dict, context_dict, result_queue):
    try:
        # Resource limits cause issues on GitHub Actions → make them optional
        try:
            import resource
            resource.setrlimit(resource.RLIMIT_CPU, (15, 15))
            resource.setrlimit(resource.RLIMIT_AS, (200 * 1024 * 1024, 200 * 1024 * 1024))
        except Exception:
            pass  # Ignore on CI / non-Unix systems

        exec(code, globals_dict, context_dict)
        result_queue.put({"status": "success", "storage": context_dict.get("storage")})
    except Exception as e:
        result_queue.put({"status": "error", "error": str(e)})

class ContractMachine:
    """
    A minimal execution environment for Python-based smart contracts.
    WARNING: Still not production-safe. For educational use only.
    """

    def __init__(self, state):
        self.state = state

    def execute(self, contract_address, sender_address, payload, amount):
        """
        Executes the contract code associated with the contract_address.
        """
        account = self.state.get_account(contract_address)
        if not account:
            return False

        code = account.get("code")
        storage = dict(account.get("storage", {}))

        if not code:
            return False

        if not self._validate_code_ast(code):
            return False

        safe_builtins = {
            "True": True, "False": False, "None": None,
            "range": range, "len": len, "min": min, "max": max,
            "abs": abs, "str": str, "bool": bool, "float": float,
            "list": list, "dict": dict, "tuple": tuple, "sum": sum,
            "Exception": Exception,
        }

        globals_for_exec = {"__builtins__": safe_builtins}

        context = {
            "storage": storage,
            "msg": {
                "sender": sender_address,
                "value": amount,
                "data": payload,
            },
        }

        try:
            # More generous timeout + no aggressive resource limits for CI
            queue = multiprocessing.Queue()
            p = multiprocessing.Process(
                target=_safe_exec_worker,
                args=(code, globals_for_exec, context, queue)
            )
            p.start()
            p.join(timeout=15)          # ← Increased for GitHub Actions

            if p.is_alive():
                p.kill()
                p.join()
                logger.error("Contract execution timed out")
                return False

            try:
                result = queue.get(timeout=2)
            except Exception:
                logger.error("Contract execution crashed without result")
                return False

            if result["status"] != "success":
                logger.error(f"Contract Execution Failed: {result.get('error')}")
                return False

            # Validate storage is JSON serializable
            try:
                json.dumps(result["storage"])
            except (TypeError, ValueError):
                logger.error("Contract storage not JSON serializable")
                return False

            self.state.update_contract_storage(contract_address, result["storage"])
            return True

        except Exception:
            logger.error("Contract Execution Failed", exc_info=True)
            return False

    def _validate_code_ast(self, code):
        """Reject code that uses double underscores or introspection."""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
                    logger.warning("Rejected contract code with double-underscore attribute access.")
                    return False
                if isinstance(node, ast.Name) and node.id.startswith("__"):
                    logger.warning("Rejected contract code with double-underscore name.")
                    return False
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    logger.warning("Rejected contract code with import statement.")
                    return False
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == 'type':
                        logger.warning("Rejected type() call.")
                        return False
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"getattr", "setattr", "delattr"}:
                    logger.warning(f"Rejected direct call to {node.func.id}.")
                    return False
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    if "__" in node.value:
                        logger.warning("Rejected string literal with double-underscore.")
                        return False
                if isinstance(node, ast.JoinedStr): # f-strings
                    logger.warning("Rejected f-string usage.")
                    return False
            return True
        except SyntaxError:
            return False
