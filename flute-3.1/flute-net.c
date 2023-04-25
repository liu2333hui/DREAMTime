#include <stdio.h>
#include <stdlib.h>
#include "flute.h"

//#define REMOVE_DUPLICATE_PIN 1

int main()
{
    int d=0;
    int x[MAXD], y[MAXD];
    Tree t;
    int flutewl;
    
    while (!feof(stdin)) {
        scanf("%d %d\n", &x[d], &y[d]);
        d++;
    }
    readLUT("POWV9.dat", "POST9.dat");

    t = flute(d, x, y, ACCURACY);
    printf("FLUTE wirelength = %d\n", t.length);
    //printtree(t);

    flutewl = flute_wl(d, x, y, ACCURACY);
    printf("FLUTE wirelength (without RSMT construction) = %d\n", flutewl);

    //plottree(t);
    return 0;
   
    int i;
    for (i=0; i<t.deg; i++)
        printf("%4g\t%4g\t%d\n",
               (float) t.branch[i].x, (float) t.branch[i].y, t.branch[i].n);
    for (i=t.deg; i<2*t.deg-2; i++)
        printf("%4g\t%4g\t%d\n",
               (float) t.branch[i].x, (float) t.branch[i].y, t.branch[i].n);
    printf("\n");

}
