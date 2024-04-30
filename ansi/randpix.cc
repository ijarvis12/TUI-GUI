#include <stdio.h>
#include <string.h>

int main() {

        struct foreground {
                char black[8] = "\e[30m";
                char red[8] = "\e[31m";
                char green[8] = "\e[32m";
                char yellow[8] = "\e[33m";
                char blue[8] = "\e[34m";
                char magenta[8] = "\e[35m";
                char cyan[8] = "\e[36m";
                char white[8] = "\e[37m";
                char* rgb(unsigned char r, unsigned char g, unsigned char b) {
                        char buffer[21];
                        sprintf(buffer, "\e[38;2;%u;%u;%um", r, g, b);
                        return buffer;
                }
        } fg;

        struct background {
                char black[8] = "\e[40m";
                char red[8] = "\e[41m";
                char green[8] = "\e[42m";
                char yellow[8] = "\e[43m";
                char blue[8] = "\e[44m";
                char magenta[8] = "\e[45m";
                char cyan[8] = "\e[46m";
                char white[8] = "\e[47m";
                char* rgb(unsigned char r, unsigned char g, unsigned char b) {
                        char buffer[21];
                        sprintf(buffer, "\e[48;2;%u;%u;%um", r, g, b);
                        return buffer;
                }
        } bg;

        struct utilities {
                // attributes
                char reset[8] = "\e[0m";
                char bold[8] = "\e[1m";
                char underline[8] = "\e[4m";
                char blink[8] = "\e[5m";
                char reverse[8] = "\e[7m";
                // clear functions
                char clear[8] = "\e[2J";
                char clearline[8] = "\e[2K";
                // cursor attributes
                char cursor_disable[8] = "\e[?25l";
                char cursor_enable[8] = "\e[?25h";
                char wrap_disable[8] = "\e[?7l";
                char wrap_enable[8] = "\e[?7h";
                // cursor movements
                char up[8] = "\e[1A";
                char down[8] = "\e[1B";
                char right[8] = "\e[1C";
                char left[8] = "\e[1D";
                char nextline[8] = "\e[1E";
                char prevline[8] = "\e[1F";
                char top[8] = "\e[0;0H";
                // sixel begin/end
                char sixel_begin[8] = "\ePq";
                char sixel_end[8] = "\e\\";
                // functions
                void init() {
                        printf("%s%s%s%s%s", reset, clear, top, cursor_disable, wrap_disable);
                }
                void end() {
                        printf("%s%s%s%s%s", reset, clear, top, cursor_enable, wrap_enable);
                }
                void to(unsigned short x, unsigned short y) {
                        printf("\e[%u;%uH", y, x);
                }
                void pause() {
                        struct foreground fg;
                        printf("%s%s", reset, fg.white);
                        char garbage;
                        scanf("%c", &garbage);
                }
                void set_pixel(unsigned short x, unsigned short y, unsigned char r, unsigned char g, unsigned char b, bool blnk) {
                        struct foreground fg;
                        to(x, y);
                        char if_blink[8] = "";
                        if(blnk) strcpy(if_blink, blink);
                        else strcpy(if_blink, reset);
                        printf("%s%s@", if_blink, fg.rgb(r, g, b));
                }
                void set_sixel(unsigned short x, unsigned short y, unsigned char r, unsigned char g, unsigned char b, unsigned short repeat, char ch) {
                        to(x, y);
                        printf("%s#0;2;%u;%u;%u#0!%u%c%s", sixel_begin, r, g, b, repeat, ch, sixel_end);
                }
        } util;

        util.init();

        for(unsigned short y=1; y<101; y++) {
                for(unsigned short x=1; x<101; x++) {
                        util.set_sixel(x, y, y-x, x, 100-y, 1, '~');
                }
        }

        util.pause();

        util.end();

        return 0;

}
