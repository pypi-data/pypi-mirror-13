Usage
Run the program from terminal as:

    gitbit <option> <directory>


<option> can be :

-s for status

-l for log

-r for hard reset

-i for initialization

-c for clone

-p for pulling from master branch

It can be left blank to do an Add->Commit->Push to the master branch.

<directory> can either be a relative or an absolute directory OR it can be left blank to run the package in the pwd(Present Working Directory)



Example:

        #with python wrapper
        gitbit -i ~/Documents/abc   # Results in the directory abc/ being initialized as a git repo
        gitbit -l                   # Will display the git log of the pwd
        gitbit -c                   # Will prompt for a url and then clone that repo in the pwd
        gitbit -p ~/Documents/Code  # Will pull your code from the remote repo into the local git repo 
        gitbit                      # Will add, commit, push everything in the pwd to its remote repo
