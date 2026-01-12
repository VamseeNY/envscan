from pathlib import Path
import os


def is_hidden(path: Path) -> bool:
    """Return True if a file or directory is considered hidden.
    Works cross-platform (filename starts with '.' on Unix or has hidden attribute on Windows).
    """
    try:
        name = path.name
        if name.startswith('.'):
            return True
        # On Windows, check FILE_ATTRIBUTE_HIDDEN
        if os.name == 'nt':
            try:
                import ctypes
                attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
                if attrs != -1:
                    return bool(attrs & 2)  # FILE_ATTRIBUTE_HIDDEN == 0x2
            except Exception:
                pass
    except Exception:
        return False
    return False


def safe_stat(path: Path):
    try:
        return path.stat()
    except Exception:
        return None
