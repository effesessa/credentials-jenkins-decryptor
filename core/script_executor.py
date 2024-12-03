class ScriptExecutor:

    def __init__(self, jenkins_requestor):
        self.jenkins_requestor = jenkins_requestor

    def build_script(self, path, replacements):
        with open(path, 'r') as file:
            script_template = file.read()
        for key, value in replacements.items():
            script_template = script_template.replace(key, value)
        return script_template

    def execute(self, path, replacements):
        script = self.build_script(path, replacements)
        response = self.jenkins_requestor.post(script)
        return response
