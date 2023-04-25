#include <stdio.h>
#include <stdlib.h>
#include "flute.h"

//#define REMOVE_DUPLICATE_PIN 1

#define MAXD 10    // max. degree that can be handled
#define ACCURACY 2  // Default accuracy
#define ROUTING 1   // 1 to construct routing, 0 to estimate WL only
#define LOCAL_REFINEMENT 0      // Suggestion: Set to 1 if ACCURACY >= 5
#define REMOVE_DUPLICATE_PIN 1  // Remove dup. pin for flute_wl() & flute()


int main()
{
    int d=0;
    int x[MAXD], y[MAXD];
    Tree t;
    int flutewl;
    
    while (!feof(stdin)) {
        scanf("%d %d\t", &x[d], &y[d]);
        d++;
    }
    readLUT("/home/liu2333hui/DREAMPlace/thirdparty/flute-3.1/build/POWV9.dat", "/home/liu2333hui/DREAMPlace/thirdparty/flute-3.1/build/POST9.dat");
   t = flute(d, x, y, ACCURACY);
    //printf("FLUTE wirelength = %d\n", t.length);
    //printtree(t);

    //flutewl = flute_wl(d, x, y, ACCURACY);
    //printf("FLUTE wirelength (without RSMT construction) = %d\n", flutewl);

    //plottree(t);
    //return 0;
   
    
    int i;
    for (i=0; i<t.deg; i++)
        printf("%4g\t%4g\t%d\n",
               (float) t.branch[i].x, (float) t.branch[i].y, t.branch[i].n);
    for (i=t.deg; i<2*t.deg-2; i++)
        printf("%4g\t%4g\t%d\n",
               (float) t.branch[i].x, (float) t.branch[i].y, t.branch[i].n);
    //printf("\n");

}
