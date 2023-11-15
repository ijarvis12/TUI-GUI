#include <cdk/cdk.h>
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
        char ps1[17] = "me@mycomputer $ ";

        //make entry widget and display it
        CDKENTRY *entrywdgt = newCDKEntry(cdkscreen, startcol, startrow, "", ps1, 0, 0, vMIXED, 32, 0, 30, false, false);
        drawCDKEntry(entrywdgt, false);
        refreshCDKScreen(cdkscreen);

        //command var
        char command[32] = {};
        char *cmd = command;

        //program end command
        char end_cmd[5] = "exit";

        //error string
        char err[256] = "err: ";

        //loop for command exec
        while(strcmp(command, end_cmd)) {
                //get command
                for(int i=0; i<32; i++) command[i] = 0;
                cmd = activateCDKEntry(entrywdgt, NULL);
                for(int i=0; i<strlen(cmd); i++) command[i] = cmd[i];

                //exec command, with error catching
                if (execCDKSwindow(swindow, command, BOTTOM)) {
                        addCDKSwindow(swindow, strcat(err, command), BOTTOM);
                        strcpy(err, "err: ");
                }

                //clear entry widget
                cleanCDKEntry(entrywdgt);
        }

        //end program
        destroyCDKSwindow(swindow);
        endCDK();
        return 0;
}
