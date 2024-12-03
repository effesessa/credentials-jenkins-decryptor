import com.cloudbees.plugins.credentials.Credentials
import com.cloudbees.plugins.credentials.CredentialsProvider
import jenkins.model.Jenkins

def searchString = 'STR'

def allCredentials = CredentialsProvider.lookupCredentials(
    Credentials.class,
    Jenkins.instance,
    null,
    null
)

def matchingCredentials = allCredentials.findAll { it.id.toLowerCase().contains(searchString.toLowerCase())  }
matchingCredentials.sort{ a, b -> a.id <=> b.id }

if (matchingCredentials) {
    println "Found ID credentials that contains ${searchString}:"
    matchingCredentials.each { cred ->
        println "${cred.id}"
    }
    print ""
} else {
    println "Not found credentials ID that contains ${searchString}"
}
