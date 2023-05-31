#include <cdk.h>
#include <string.h>

int main(){
        //initialize
        WINDOW *screen = initscr();
        CDKSCREEN *cdkscreen = initCDKScreen(screen);
        raw();
        echo();

        //starting place for swindow
        int startrow = 1;
        int startcol = 1;

        //make swindow and display it
        CDKSWINDOW *swindow = newCDKSwindow(cdkscreen, startrow, startcol, 25, 50, "== Terminal ==", 1000, true, true);
        drawCDKSwindow(swindow, true);

        //move cursor to swindow
        move(startrow+=26, ++startcol);

        //refresh screen
        refreshCDKScreen(cdkscreen);

        //command var
        char command[256] = {};

        //program end command (ESC)
        char end_cmd[5] = "exit";

        //error string
        char err[256] = "err: ";

        //loop for command exec
        while(!getstr(command) && strcmp(command, end_cmd)) {
                //exec command
                if (execCDKSwindow(swindow, command, BOTTOM)) {
                        addCDKSwindow(swindow, strcat(err, command), BOTTOM);
                        strcpy(err, "err: ");
                }
                //move cursor back to cmdline
                move(startrow, startcol);
                //refresh screen
                refreshCDKScreen(cdkscreen);
                //clear command var
                strcpy(command, "");
        }

        //end program
        destroyCDKSwindow(swindow);
        endCDK();
        return 0;
}
