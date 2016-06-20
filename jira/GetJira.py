#http://jira.readthedocs.org/en/latest/index.html?highlight=time#examples

import jira as j
import sys  
import csv
import MySQLdb


reload(sys)  
sys.setdefaultencoding('utf8')


def printlist(x):
    cout = ""
    for c in x:
        cout = cout + "," + c.body.encode("utf-8")
    return cout


def GetVersionInfo(versions):
    x = []
    for version in versions:
        x.append(version.name)
    return x


def checkNull(x):
    if x is None:
        return "N/A"
    else:
        return x.encode("utf-8")

DB = csv.writer(open('onos.jira.bugs.cvs', 'wb'))
ComDB = csv.writer(open('onos.jira.comments.cvs', 'wb'))
VerDB = csv.writer(open('onos.jira.version.cvs', 'wb'))
jira = j.JIRA('https://jira.onosproject.org')
#issue = jira.issue('JRA-9')

i = 0
resultsSize = 1000

while resultsSize == 1000:
    results = jira.search_issues('', startAt=i, maxResults=i+1000)
    resultsSize = len(results)
    for issue in results:
        field = issue.fields
        print issue.key
        comment_list = printlist(jira.comments(issue))
        #activity_list = printlist(issue.components)
        #for component in issue.fields.components:
        #  print component.name
        res_id = field.resolution is None and  "N/A" or  field.resolution.id
        res_date = field.resolutiondate is None and "N/A" or field.resolutiondate
        verList = [issue.id]
        verList = verList + GetVersionInfo(issue.fields.versions)
        #  verList =  verList + GetVersionInfo(issue.versions)
        VerDB.writerow(verList)
        DB.writerow([issue.id,
                     str(MySQLdb.escape_string(issue.key)),
                     str(MySQLdb.escape_string(checkNull(field.description))),
                     str(MySQLdb.escape_string(checkNull(field.summary))),
                     str(MySQLdb.escape_string(field.issuetype.name.encode("utf-8"))),
                     field.priority.id, field.status.id, res_id, field.created, res_date])

        for tag in field.labels:
            pass
            #do tag stuff
            #tag
            #field.epic_link

    for comment in jira.comments(issue):
        ComDB.writerow([issue.id, comment.id,
                        str(MySQLdb.escape_string(comment.raw['author']['name'])),
                        comment.updated, comment.created,
                        str(MySQLdb.escape_string(comment.body.encode("utf-8")))])

    print len(results)
    i=i + resultsSize
#print issue.fields.project.key # 'JRA'
#print issue.fields.issuetype.name # 'New Feature'
#print issue.fields.reporter.displayName # 'Mike Cannon-Brookes [Atlassian]'
