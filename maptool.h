#ifndef MAPTOOL_H
#define MAPTOOL_H

/* set by the user */
#define OPAQUE_FLAG          (1<<0)		/* cell blocks light (cannot see-through) */
#define WALKABLE_FLAG        (1<<1)		/* cell can be passed (used for path-finding) */
#define MONSTER_FLAG         (1<<2)		/* a monster is at this cell */
#define ITEM_FLAG            (1<<3)		/* an item is lying at this cell */

/* derive information: calculated by maptool */
#define VISIBLE_FLAG         (1<<16)		/* cell was visible after last maptool_calculate_fov call */
#define EXPLORED_FLAG        (1<<17)		/* cell is or has been visible */

/* main object */
struct MapTool {
	int width, height;
	unsigned int *flags;

	int *distance_map; /* the calculated distance map */

	/* temporary storage for distance map calculation */
	int expa_size, expa_capa, *expa_x, *expa_y, *expa_dist;
};

/* construction, get & set flags */
struct MapTool *maptool_new(int width, int height);
void maptool_delete(struct MapTool *mt);
void maptool_set_flag(struct MapTool *mt, int x, int y, unsigned int flag_mask, int flag);
int maptool_get_flag(struct MapTool *mt, int x, int y, unsigned int flag_mask);

/* calculate field of vision */
void maptool_calculate_fov(struct MapTool *mt, int x, int y, int radius);

/* calculate distance map */
int maptool_get_distance_map(struct MapTool *dm, int x, int y);
void maptool_get_distance_map_dir(struct MapTool *dm, int x, int y, int *dx, int *dy);
void maptool_calculate_distance_map(struct MapTool *dm, int *xs, int *ys, int n);

#endif
