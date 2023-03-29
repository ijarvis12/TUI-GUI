#include <cdk/cdk.h>

int main(){
        //initialize
        WINDOW *screen = initscr();
        CDKSCREEN *cdkscreen = initCDKScreen(screen);
        raw();
        echo();

        //starting place for swindow
        int startrow = 1;
        int startcol = 1;

        //make swindow and display
        CDKSWINDOW *swindow = newCDKSwindow(cdkscreen,startrow,startcol,25,50,"Terminal",1000,true,true);
        drawCDKSwindow(swindow,true);

        //move cursor inside swindow
        move(startrow,startcol++);

        //refresh screen
        refreshCDKScreen(cdkscreen);

        //command var
        char command[256] = {};

        //loop for command exec
        do {
                //clear command var
                strcpy(command,"");
                //move cursor down
                move(startrow+=2,startcol);
                //get command
                getstr(command);
                addCDKSwindow(swindow,command,BOTTOM);
                refreshCDKScreen(cdkscreen);
                //exec command
                execCDKSwindow(swindow,command,BOTTOM);
                refreshCDKScreen(cdkscreen);
        }
        while(strcmp(command, "^C") != 0);

        //end program
        destroyCDKSwindow(swindow);
        endCDK();
        return 0;
}
