#include <cdk.h>
#include <string.h>

int main(void) {
        //initialize
        WINDOW *screen = initscr();
        CDKSCREEN *cdkscreen = initCDKScreen(screen);
        raw();
        echo();

        //starting place for swindow
        int startrow = 1;
        int startcol = 1;

        //make swindow and display it
        CDKSWINDOW *swindow = newCDKSwindow(cdkscreen, startcol, startrow, 25, 50, "-- Terminal --", 1000, true, true);
        drawCDKSwindow(swindow, true);

        //cmdline PS1
        startcol++;
        startrow += 26;
        char ps1[18] = "me@mycomputer $ ";

        //command var
        char command[256] = {};

        //program end command
        char end_cmd[5] = "exit";

        //error string
        char err[256] = "err: ";

        //loop for command exec
        while(strcmp(command, end_cmd)) {
                //show cmdline
                refreshCDKScreen(cdkscreen);
                mvaddstr(startrow, startcol, ps1);
                
                //enter command
                strcpy(command, "");
                getstr(command);
                
                //exec command, with error catching
                if (execCDKSwindow(swindow, command, BOTTOM)) {
                        addCDKSwindow(swindow, strcat(err, command), BOTTOM);
                        strcpy(err, "err: ");
                }
        }

        //end program
        destroyCDKSwindow(swindow);
        endCDK();
        return 0;
}
