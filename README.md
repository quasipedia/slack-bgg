# slack-bgg
A slack integration allowing to interact with BoardGameGeek.com.

The app is a web application (essentially a thin layer between BoardGameGeek
and Slack API's), so it requires to be installed (and served) on a machine that
has access to (and can be accessed from) the Internet.

Currently it support two functionalities:

  - Searches (echoed to the user issuing the command)
  - Game details (echoed to the entire channel the user is in)


## Usage

Check the `application/help.md` for up-to date command syntax.  The name of the
actual command (e.g.: `/bgg`) will depend by how you set up the integration in
the Slack control panel.


## Installation

`slack-bgg` is a python WSGI application.  You can serve it the way you prefer
(apache, nginx, gunicorn, uWSGI)...  For your convenience, there's a handy
playbook that allows to get up and running in no time, but please be advised
the roles have been written targeting a fresh CentOS 7 virtual machine, so
*you want to review them thoroughly* if you are going to run them onto a
machine that hosts other web content...

The easiest way to run the playbook is:

    ansible-playbook ansible/slack-bgg.yml -i <IP-here>, --user=<user-name>


## Known limitations

*This code is the result of a hackday, so the code works but it's far from a
masterpiece*.  Among the things that annoy me the most (and that I may or may
not fix at a later stage):

  - [ ] Python 2.x rather than 3.x (CentOS has not python3 package)
  - [ ] Requests to APIs are not async (no python3 → no cake!)
  - [ ] Sorting of search results is not very useful (try to find the game ID
        of _Risk!_ or _Monopoly_ if you don't believe me!)
  - [ ] No pagination for search results

Also, limitations you should be aware that are not due to my code but to Slack
API limitations:

  - The integration will not work on private channels, if you are trying to
    display a given game information (will redirect to your slackbot channel
    instead)
  - If you query a search in a given channel, the result will be echoed into
    your slackbot chat (this may be me having missed some bit of information
    in the API documentation, though)
