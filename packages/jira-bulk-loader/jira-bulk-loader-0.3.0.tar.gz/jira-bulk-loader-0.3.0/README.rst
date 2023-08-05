Introduction
============

The key idea of jira-bulk-loader is an activity template.

The template is written in human language with a few markup rules. jira-bulk-loader.py uses the prepared template to create the corresponding set of tasks easy and effortless.


Requirements
============

#. Python 2.7, 3.4, 3.5
#. JIRA REST API version 2 (i.e. JIRA v5.0 and above)


Linux installation
==================

To install jira-bulk-loader, simply run: ::

    $ pip install jira-bulk-loader


Windows installation
====================

To install jira-bulk-loader on Windows:

#. Download and install the latest Python 2.7 - https://www.python.org/downloads/windows/
#. Run C:\\Python27\\python.exe -m pip install -U pip jira-bulk-loader
#. Run C:\\Python27\\Scripts\\jira-bulk-loader.py -h to verify installation


Very simple case
================

Template:

    | 	h5. First task summary \*assignee\*
    |	=description line 1
    | 	=description line 2
    |
    | 	h5. Second task summary \*assignee\*
    | 	=description line 3
    | 	=description line 4

command: 

	jira-bulk-loader.py -U <your_username> -P <your_password> -H jira.your_domain.org -W PRKEY template_file

two tasks will be created and assigned to *assignee* in the project with a project key *PRKEY*.



One more simple case
====================

Template:

    | 	h5. Task summary \*assignee\*
    |	=description line 1
    | 	=description line 2
    |
    | 	# First sub-task summary \*assignee1\* 
    | 	=description line 3
    |
    |	# Second sub-task summary \*assignee2\* %2012-09-18%
    | 	=description line 3

and the command:

	jira-bulk-loader.py -U <your_username> -P <your_password> -H jira.your_domain.org -D 2012-09-20 -W PRKEY template_file

It will create a task with two subtasks. Moreover it also sets due date 2012-09-18 (YYYY-mm-DD) to the 2nd sub-task, and 2012-09-20 to the task and its first sub-task.


Link issues
===========

A task can be `linked <https://jira.wargaming.net/rest/api/2/issueLinkType>`_ to another task.

    | h5. Task1 summary \*assignee\* <JIRA-1234>
    | h5. Task2 summary \*assignee\* <JIRA-1234|Relates>
    | h5. Task3 summary \*assignee\* <Blocks|JIRA-1234>

where 'Relates' and 'Blocks' are link types. If it is not specified, default value 'Relates' will be used.
For the full list of possible link types see: https://<your-JIRA-URL>/rest/api/2/issueLinkType

In this example Task1 will be included in JIRA-1234, JIRA-1234 will be blocked by Task2 and Task3 will be blocked by JIRA-1234.


Dry run option
==============

jira-bulk-loader.py has an option *--dry*. If it is specified in command line, jira-bulk-loader checks template syntax, verifies project name and assignees but doesn't create tasks.

I would strongly recommend using it every time.



User story and 'included in' tasks
==================================

Sometime an activity is too complex and it is much easier and appropriate to create several tasks with sub-tasks and link them to a user story.

    | 	h4. User story summary \*assignee\*
    |	=description
    |
    | 	h5. First task summary \*assignee1\*
    |	=description
    | 	# Sub-task summary \*assignee1\* 
    | 	=description
    |
    | 	h5. Second task summary \*assignee2\*
    |	=description
    | 	# Sub-task summary \*assignee2\* 
    | 	=description

In this case h5 tasks will be linked to h4 user story.



Create subtask of existing task or user story
==============================================

If you have a task in JIRA and want to create a subtask for it, use the following syntax:

    | ... JIRA-1234
    |   # Sub-task summary \*assignee1\*
    |   =description



Task parameters
===============

It is possible to define task attributes in template:

    |	{"project":{"key":"PRKEY"}}
    |	{"priority": {"name": "High"}}
    |	{"duedate": "2012-09-20"}
    |	{"components": [{"name": "Production"}]}
    |
    | 	h5. First task summary \*assignee1\*
    |	=description
    |
    | 	h5. Second task summary \*assignee2\* {"components": [{"name": "Localizations"}]}
    |	=description
    |
    | 	h5. Third task summary \*assignee3\*
    |	=description

In the example *project*, *priority* and *duedate* will be applied to all tasks by default. The *component* 'Production' will be applied to task 1 and 3. However, the second task will use the *component* 'Localizations'.

`This part <http://docs.atlassian.com/jira/REST/latest/#id200060>`_ of Jira documentation could give a clue how to find out relevant parameters in your project and their format.



A short summary
===============

Let me summarize what are the possible markups to begin a line with:

- a user story: h4. summary \*assignee\*
- a task: h5. summary \*assignee\*
- existing user story: .. JIRA-1234
- existing task: ... JIRA-1234
- a sub-task: # summary \*assignee\*  
- one more sub-task: #* summary \*assignee\*
- description: = 

Every task definition can be followed by one or more inline auxiliary parameters:

- %YYYY-MM-DD% - due date
- <JIRA-1234> or <JIRA-1234|Inclusion> - link
- {"components": [{"name": "Localizations"}]} - any json data that will be sent directly to JIRA API as a part of `create request <https://docs.atlassian.com/jira/REST/latest/#d2e4264>`_.



Template variables
==================

    |	[REVISION=194567]
    |	[QA=John]
    |
    | 	h5. First task summary \*$QA\*
    |	=description $REVISION
    |
    | 	h5. Second task summary \*$QA\*
    |	=description $REVISION

is equivalent to 

    | 	h5. First task summary \*John\*
    |	=description 194567
    |
    | 	h5. Second task summary \*John\*
    |	=description 194567

the important difference is that you don't need to change assignee or description of each task in your template. You change variable value instead and it is applied to every line in the template.


Run-time variables
==================

Sometime it is necessary to create a reference to another task in the template. Such requirement can be fulfilled with a help of template run-time variables.

    |  h5. h5 task1 *assignee* [TASK_KEY1]
    |  h5. h5 task2 *assignee* [TASK_KEY2]
    |  h5. h5 task3 *assignee*
    |  =description $TASK_KEY1
    |  # Sub-task *assignee*
    |  =description $TASK_KEY2

When jira-bulk-loader creates 'h5 task1' and 'h5 task2' in Jira, $TASK_KEY1 and $TASK_KEY2 will be have their issue_id.

The only restriction is: you can't reference a task that has not been created yet, i.e. a template variable cannot be used before assignment.


Issues and new ideas
====================

If you found an issue or if you have an idea of improvement please visit `https://github.com/oktopuz/jira-bulk-loader/issues <https://github.com/oktopuz/jira-bulk-loader/issues>`_


