#include "maptool.h"

#include <stdlib.h>
#include <limits.h>
#include <stddef.h>

struct MapTool *maptool_new(int width, int height)
{
	const int num_cells = width * height;

	struct MapTool *mt = (struct MapTool*)malloc(sizeof(struct MapTool));
	mt->width = width;
	mt->height = height;
	mt->flags = (unsigned int*)malloc(sizeof(unsigned int) * num_cells);
	mt->distance_map = (int*)malloc(sizeof(int) * num_cells);
	mt->expa_size = 0;
	mt->expa_capa = 0;
	mt->expa_x = NULL;
	mt->expa_y = NULL;
	mt->expa_dist = NULL;
	for (int i=0; i<num_cells; ++i) {
		mt->distance_map[i] = 0;
		mt->flags[i] = 0;
	}

	return mt;
}

void maptool_delete(struct MapTool *mt)
{
	free(mt->flags);
	free(mt->distance_map);
	free(mt->expa_x);
	free(mt->expa_y);
	free(mt->expa_dist);
	free(mt);
}

void maptool_set_flag(struct MapTool *mt, int x, int y, unsigned int flag_mask, int flag)
{
	if (x<0 || y<0 || x>=mt->width || y>=mt->height) return;
	if (flag) {
		mt->flags[x+y*mt->width] |= flag_mask;
	} else {
		mt->flags[x+y*mt->width] &= ~flag_mask;
	}
}

int maptool_get_flag(struct MapTool *mt, int x, int y, unsigned int flag_mask)
{
	if (x<0 || y<0 || x>=mt->width || y>=mt->height) return 0;
	return (mt->flags[x+y*mt->width] & flag_mask) ? 1 : 0;
}

/******************************************************************************
 * Field of vision calculation                                                *
 ******************************************************************************/

/* Algorithm: Recursive shadow casting
  (http://roguebasin.roguelikedevelopment.org/index.php?title=FOV_using_recursive_shadowcasting)

  Source code taken from
  http://roguebasin.roguelikedevelopment.org/index.php?title=PythonShadowcastingImplementation (written by Eric Burgess (?)) 
  and converted to C.
*/

static void fov_cast_light(struct MapTool *mt, int cx, int cy, int row, float start, float end, int radius, int xx, int xy, int yx, int yy)
{
	int j;
	int blocked;
	int dx, dy, X, Y;
	float l_slope, r_slope, new_start = 0;

	if (start < end) {
		return;
	}

	for (j=row; j<=radius; ++j) {
		dx = -j-1;
		dy = -j;
		blocked = 0;

		/* scan a row */
		while (dx <= 0) {
			dx += 1;
			/* Translate the dx, dy coordinates into map coordinates */
			X = cx + dx*xx + dy*xy;
			Y = cy + dx*yx + dy*yy;
			/* l_slope and r_slope store the slopes of the left and right extremities of the square we're considering */
			l_slope = (dx-0.5)/(dy+0.5);
			r_slope = (dx+0.5)/(dy-0.5);
			if (start < r_slope) {
				continue;
			} else if (end > l_slope) {
				break;
			} else {
				/* Our light beam is touching this square; light it */
				if (dx*dx + dy*dy < radius*radius && X>0 && Y>0 && X<mt->width && Y<mt->height) {
					/* see cell (X,Y) */
					maptool_set_flag(mt, X, Y, VISIBLE_FLAG | EXPLORED_FLAG, 1);
				}
				if (blocked) {
					/* we're scanning a row of blocked squares */
					if (mt->flags[X+Y*mt->width] & OPAQUE_FLAG) {
						new_start = r_slope;
						continue;
					} else {
						blocked = 0;
						start = new_start;
					}
				} else {
					if (maptool_get_flag(mt, X, Y, OPAQUE_FLAG) && j<radius) {
						/* this is a blocking square, start a child scan */
						blocked = 1;
						fov_cast_light(mt, cx, cy, j+1, start, l_slope, radius, xx, xy, yx, yy);
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

void maptool_calculate_fov(struct MapTool *mt, int x, int y, int radius)
{
	/* multipliers for transforming coordinates to other octants */
	static int mult[4][8] = {
		{1,  0,  0, -1, -1,  0,  0,  1},
		{0,  1, -1,  0,  0, -1,  1,  0},
		{0,  1,  1,  0,  0, -1, -1,  0},
		{1,  0,  0,  1, -1,  0,  0, -1}
	};

	for (int i=0; i<mt->width; ++i) {
		for (int j=0; j<mt->height; ++j) {
			maptool_set_flag(mt, i, j, VISIBLE_FLAG, 0);
		}
	}

	maptool_set_flag(mt, x, y, VISIBLE_FLAG | EXPLORED_FLAG, 1);

	for (int i=0; i<8; ++i) {
		fov_cast_light(mt, x, y, 1, 1.0, 0.0, radius, mult[0][i], mult[1][i], mult[2][i], mult[3][i]);
	}
}

/******************************************************************************
 * Distance (Dijkstra) maps                                                   *
 ******************************************************************************/

#define UNEXPLORED (-1)
#define EXPANDED (-2)

int maptool_get_distance_map(struct MapTool *mt, int x, int y)
{
	const int width = mt->width, height = mt->height;
	if (x<0 || y<0 || x>=width || y>=height) return UNEXPLORED;
	return mt->distance_map[x+y*width];
}

void maptool_get_distance_map_dir(struct MapTool *mt, int x, int y, int *dx, int *dy)
{
	int min_dist = INT_MAX;

	*dx = 0;
	*dy = 0;

	/* is (x,y) not accessable? */
	if (maptool_get_distance_map(mt, x, y) < 0) {
		return;
	}

	/* we prefer non-diagonal directions, so we check them last */
	int dirs[8][2] = { {-1,-1},{+1,-1},{-1,+1},{+1,+1}, {0,-1},{-1,0},{+1,0},{0,+1} };
	for (int i=0; i<8; ++i) {
		int dist = maptool_get_distance_map(mt, x+dirs[i][0], y+dirs[i][1]);
		if (dist >= 0 && dist <= min_dist) {
			min_dist = dist; *dx = dirs[i][0]; *dy = dirs[i][1];
		}
	}
}

static void maptool_expand_distance_map(struct MapTool *mt, int x, int y, int dist)
{
	const int w = mt->width;

	int i = mt->expa_size;
	if (i >= mt->expa_capa) {
		if (mt->expa_capa == 0) 
			mt->expa_capa = 256;
		else
			mt->expa_capa *= 2;
		size_t new_size = sizeof(int) * mt->expa_capa;
		mt->expa_x = (int*)realloc(mt->expa_x, new_size);
		mt->expa_y = (int*)realloc(mt->expa_y, new_size);
		mt->expa_dist = (int*)realloc(mt->expa_dist, new_size);
	}

	/* mark as expanded */
	mt->distance_map[x+y*w] = EXPANDED;

	/* append (x,y,dist) right */
	mt->expa_x[i] = x;
	mt->expa_y[i] = y;
	mt->expa_dist[i] = dist;
	mt->expa_size += 1;

	/* bubble left until sorted */
	while (i>0 && mt->expa_dist[i-1]<dist) {
		int tmp;
		tmp = mt->expa_x[i]; mt->expa_x[i] = mt->expa_x[i-1]; mt->expa_x[i-1] = tmp;
		tmp = mt->expa_y[i]; mt->expa_y[i] = mt->expa_y[i-1]; mt->expa_y[i-1] = tmp;
		tmp = mt->expa_dist[i]; mt->expa_dist[i] = mt->expa_dist[i-1]; mt->expa_dist[i-1] = tmp;
		--i;
	}
}

static void maptool_distance_map_expanded_pop(struct MapTool *mt, int *x, int *y, int *dist)
{
	int last = mt->expa_size-1;
	*x = mt->expa_x[last]; *y = mt->expa_y[last]; *dist = mt->expa_dist[last];
	mt->expa_size -= 1;
}

static int maptool_distance_map_expanded_empty(struct MapTool *mt)
{
	return mt->expa_size == 0;
}

static void maptool_explore_distance_map(struct MapTool *mt, int x, int y, int dist)
{
	const int w = mt->width;

	/* explore (x,y) */
	mt->distance_map[x+y*w] = dist;

	/* expand unexplored neighbors (that are walkable) to unexpanded-list */
	for (int X=x-1; X<=x+1; ++X)
	for (int Y=y-1; Y<=y+1; ++Y) {
		if (X<0 || Y<0 || X>=mt->width || Y>=mt->height) continue;
		if (maptool_get_flag(mt, X, Y, WALKABLE_FLAG)) {
			int neighbor_dist = mt->distance_map[X+Y*w];
			if (neighbor_dist == UNEXPLORED) {
				mt->distance_map[X+Y*w] = EXPANDED;
				maptool_expand_distance_map(mt, X, Y, dist+1);
			}
			//assert(neighbor_dist <= dist) ??
		}
	}
}

void maptool_calculate_distance_map(struct MapTool *mt, int *xs, int *ys, int n)
{
	const int w=mt->width, h=mt->height;

	/* reset map */
	mt->expa_size = 0;
	for (int y=0; y<h; ++y) {
		for (int x=0; x<w; ++x) {
			mt->distance_map[x+y*w] = UNEXPLORED;
		}
	}

	/* insert goal points (xs[], ys[]). (explore with distance 0). */
	for (int i=0; i<n; ++i) {
		maptool_explore_distance_map(mt, xs[i], ys[i], 0);
	}

	/* expand neighbors */
	while (!maptool_distance_map_expanded_empty(mt)) {
		int x, y, dist;
		maptool_distance_map_expanded_pop(mt, &x, &y, &dist);
		maptool_explore_distance_map(mt, x, y, dist);
	}
}

#undef UNEXPLORED
#undef EXPANDED
