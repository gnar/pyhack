#include "cmap.h"

#include <stdlib.h>
#include <stdio.h>

static void array_append(int **arr, int *size, int *capa, int item)
{
	int i = *size;

	(*size) += 1;
	if (*capa < *size) {
		if (*capa == 0) *capa = 128;
		while (*capa < *size) (*capa) *= 2;
		*arr = (int*)realloc(*arr, sizeof(int) * (*capa));
	}
	(*arr)[i] = item;
}

/* DISTANCE MAPS */

#define UNEXPLORED (-1)
#define OBSTRUCTED (-2)
#define EXPANDED (-3)

void calculate_distance_map(
	int width, int height, unsigned int *flags, unsigned int flag, unsigned mask,
	int *xs, int *ys, int n, 
	int *dist_map)
{
	int *src=NULL; int src_size=0, src_capa=0;
	int *dst=NULL; int dst_size=0, dst_capa=0;

	/* reset map */
	for (int i=0; i<width*height; ++i) {
		unsigned int is_walkable = (flags[i] & mask) == (flag & mask);
		dist_map[i] = is_walkable ? UNEXPLORED : OBSTRUCTED;
	}

	/* pre-expand goal points (xs[], ys[]) with distance 0. */
	for (int i=0; i<n; ++i) {
		array_append(&src, &src_size, &src_capa, xs[i] + ys[i]*width);
	}

	int dist = 0; /* distance of expanded cells in src */
	while (src_size > 0) {
		for (int i=0; i<src_size; ++i) {
			int idx = src[i];
			int x = idx % width;
			int y = idx / width;

			/* explore */
			dist_map[idx] = dist;

			/* expand */
			for (int Y=y-1; Y<=y+1; ++Y) {
				if (Y < 0 || Y >= height) continue;
				for (int X=x-1; X<=x+1; ++X) {
					if (X < 0 || X >= width) continue;
					int IDX = X + Y*width;
					if (dist_map[IDX] == UNEXPLORED) {
						dist_map[IDX] = EXPANDED;
						array_append(&dst, &dst_size, &dst_capa, IDX);
					}
				}
			}
		}

		/* swap src and dst, then clear dst. */
		int *tmp0 = src; src = dst; dst = tmp0;
		int tmp1 = src_capa; src_capa = dst_capa; dst_capa = tmp1;
		src_size = dst_size; dst_size = 0;

		dist += 1;
	}

	free(src);
	free(dst);
}

/* FOV */

static void cast_light(
	int width, int height, unsigned int *flags, unsigned int flag, unsigned int mask,
	int cx, int cy, int row, float start, float end, int radius, 
	int xx, int xy, int yx, int yy,
	int *xs, int *ys, int *n, int *tmp)
{
	if (start < end) return;

	for (int j=row; j<=radius; ++j) {
		int dx = -j-1, dy = -j;
		int blocked = 0;

		/* scan a row */
		while (dx <= 0) {
			dx += 1;

			/* Translate the dx, dy coordinates into map coordinates */
			int X = cx + dx*xx + dy*xy;
			int Y = cy + dx*yx + dy*yy;

			/* l_slope and r_slope store the slopes of the left and right extremities of the square we're considering */
			float l_slope = (dx-0.5)/(dy+0.5);
			float r_slope = (dx+0.5)/(dy-0.5);

			float new_start;
			if (start < r_slope) {
				continue;
			} else if (end > l_slope) {
				break;
			} else {
				int IDX = X+Y*width;
				/* Our light beam is touching this square; light it */
				if (dx*dx + dy*dy < radius*radius && X>=0 && Y>=0 && X<width && Y<height) {
					/* see cell (X,Y) */
					if (tmp[IDX] == 0) {
						tmp[IDX] = 1;
						xs[*n] = X; ys[*n] = Y; (*n) += 1;
					}
				}
				if (blocked) {
					/* we're scanning a row of blocked squares */
					if ((flags[IDX] & mask) != (flag & mask)) {
						new_start = r_slope;
						continue;
					} else {
						blocked = 0;
						start = new_start;
					}
				} else {
					if (((flags[IDX] & mask) != (flag & mask)) && j<radius) {
						/* this is a blocking square, start a child scan */
						blocked = 1;
						cast_light(width, height, flags, flag, mask, cx, cy, j+1, start, l_slope, radius, xx, xy, yx, yy, xs, ys, n, tmp);
						new_start = r_slope;
					}
				}
			}
		}

		/* Row is scanned; do next row unless last square was blocked */
		if (blocked) {
			break;
		}
	}
}

int calculate_fov(
	/* input */
	int width, int height, unsigned int *flags, unsigned int flag, unsigned int mask,
	int x, int y, int radius,

	/* output */
	int *xs, int *ys)
{
	int n = 0;
	int *tmp = calloc(width*height, sizeof(int));

	/* multipliers for transforming coordinates to other octants */
	static int mult[4][8] = {
		{1,  0,  0, -1, -1,  0,  0,  1},
		{0,  1, -1,  0,  0, -1,  1,  0},
		{0,  1,  1,  0,  0, -1, -1,  0},
		{1,  0,  0,  1, -1,  0,  0, -1}
	};

	/* see (x,y) */
	xs[n] = x; ys[n] = y; ++n;

	/* scan octants */
	for (int i=0; i<8; ++i) {
		cast_light(width, height, flags, flag, mask, x, y, 1, 1.0, 0.0, radius, mult[0][i], mult[1][i], mult[2][i], mult[3][i], xs, ys, &n, tmp);
	}

	free(tmp);

	return n;
}
