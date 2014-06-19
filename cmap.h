#ifndef DISTMAP_H
#define DISTMAP_H

void calculate_distance_map(
	int width, int height, unsigned int *flags, unsigned int flag, unsigned mask,
	int *xs, int *ys, int n, 
	int *dist_map
);

int calculate_fov(
	/* input */
	int width, int height, unsigned int *flags, unsigned int flag, unsigned int mask,
	int x, int y, int radius,

	/* result */
	int *xs, int *ys
);

#endif
