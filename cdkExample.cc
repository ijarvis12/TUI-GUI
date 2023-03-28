#include <cdk/cdk.h>

int main(){
        WINDOW *screen = initscr();
        CDKSCREEN *cdkscreen = initCDKScreen(screen);
        raw();
        echo();
        int startx = 1;
        int starty = 1;
        CDKSWINDOW *swindow = newCDKSwindow(cdkscreen,startx,starty,25,50,"Hello, World",1000,true,true);
        drawCDKSwindow(swindow,true);
        move(startx+=2,starty++);
        refreshCDKScreen(cdkscreen);
        char command[256] = {};
        do {
                strcpy(command,"");
                move(startx++,starty);
                getstr(command);
                addCDKSwindow(swindow,command,BOTTOM);
                refreshCDKScreen(cdkscreen);
                //execCDKSwindow(swindow,command,**getCDKSwindowContents(swindow,NULL));
                refreshCDKScreen(cdkscreen);
        }
        while(strcmp(command, "^C") != 0);
        destroyCDKSwindow(swindow);
        endCDK();
        return 0;
}
