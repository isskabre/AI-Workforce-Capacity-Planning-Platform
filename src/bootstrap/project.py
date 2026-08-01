from .workspace import register_workspace_src


def bootstrap_project():

    src = register_workspace_src()

    print("=" * 70)
    print("AI Workforce Capacity Planning Platform")
    print("=" * 70)
    print(f"Project source : {src}")
    print("Bootstrap      : PASSED")
    print("=" * 70)

    return src