#include <cdk/cdk.h>

int main(){
        WINDOW *screen = initscr();
        CDKSCREEN *cdkscreen = initCDKScreen(screen);
        raw();
        echo();
        CDKSWINDOW *swindow = newCDKSwindow(cdkscreen,CENTER,CENTER,50,100,"Hello, World",1000,true,true);
        drawCDKSwindow(swindow,true);
        refreshCDKScreen(cdkscreen);
        char command[256] = {};
        do {
                strcpy(command,"");
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
