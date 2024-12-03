import com.cloudbees.plugins.credentials.CredentialsProvider
import com.cloudbees.plugins.credentials.domains.Domain
import com.cloudbees.plugins.credentials.common.StandardUsernamePasswordCredentials
import org.jenkinsci.plugins.plaincredentials.StringCredentials
import org.jenkinsci.plugins.plaincredentials.FileCredentials
import org.jenkinsci.plugins.github_branch_source.GitHubAppCredentials
import jenkins.model.Jenkins

def credentialId = 'CREDENTIAL_ID'

def credentialObject = CredentialsProvider.lookupCredentials(
    com.cloudbees.plugins.credentials.Credentials.class,
    Jenkins.instance,
    null,
    null
).find { it.id.equalsIgnoreCase(credentialId) }

if (credentialObject) {
    if (credentialObject instanceof GitHubAppCredentials) {
        className = credentialObject.getClass().getName()
        print "Class $className instance not supported!"
    }
    else if(credentialObject instanceof StandardUsernamePasswordCredentials){
        println "Type: StandardUsernamePasswordCredentials"
        println "Username: " + credentialObject.username + "\nPassword: " + credentialObject.password.getPlainText()
    }
    else if (credentialObject instanceof StringCredentials) {
        println "Type: StringCredentials"
        println(credentialObject.secret.getPlainText())
    }
    else if (credentialObject instanceof FileCredentials) {
        println "Type: FileCredentials"
        def fileName = credentialObject.getFileName()
        def fileContent = credentialObject.getContent()
        println "${fileContent}"
    }
    else {
        className = credentialObject.getClass().getName()
        print "Class $className instance not supported!"
    }
} else {
    return "Credential $credentialId not found!"
}