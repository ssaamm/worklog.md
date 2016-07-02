# source this in your bashrc to get the `worklog` helper function

worklog() {
    WORKLOG=$HOME/worklog.md
    theDate=`date +'%d %b %Y'`
    if ! grep --quiet "$theDate" $WORKLOG
    then
        echo '' >> $WORKLOG
        echo \#\# $theDate >> $WORKLOG
        echo '- Start @ ' >> $WORKLOG
        echo '- Lunch ' >> $WORKLOG
        echo '- Stop @ ' >> $WORKLOG
    fi

    $VISUAL '+normal GA' $WORKLOG
}

alias wl=worklog
