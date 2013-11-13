/*
This file is part of "Avanor, the Land of Mystery" roguelike game
Home page: http://www.avanor.com/
Copyright (C) 2000-2003 Vadim Gaidukevich

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
*/

#include "xpotion.h"
#include "creature.h"
#include "modifer.h"

REGISTER_CLASS(XPotion);

PN_COLORTABLE pnc_table[] = {
/* 0 PNC_CLEAR*/{		"clear", 			xLIGHTGRAY		,0},
/* 1 PNC_SMOKY*/{	 	"smoky", 			xLIGHTGRAY		,0},
/* 2 PNC_GREEN*/{	 	"green", 			xGREEN			,0},
/* 3 PNC_ORANGE*/{ 		"orange", 			xYELLOW			,0},
/* 4 PNC_YELLOW*/{ 		"yellow", 			xYELLOW			,0},
/* 5 PNC_BLACK*/{	 	"black", 			xDARKGRAY		,0},
/* 6 PNC_BLUE*/{ 		"blue", 			xBLUE			,0},
/* 7 PNC_WHITE*/{	 	"white", 			xWHITE			,0},
/* 8 PNC_CYAN*/{ 		"cyan", 			xCYAN			,0},
/* 9 PNC_PURPLE*/{		"purple", 			xLIGHTMAGENTA	,0},
/* 10 PNC_HAZE*/{ 		"haze", 			xLIGHTGRAY		,0},
/* 11 PNC_GOLDEN*/{		"golden", 			xYELLOW			,0},
/* 12 PNC_SILVER*/{		"silver", 			xLIGHTGRAY		,0},
/* 13 PNC_AZURE*/{		"azure", 			xLIGHTCYAN		,0},
/* 14 PNC_MURKY*/{		"murky", 			xDARKGRAY		,0},
/* 15 PNC_RED*/	{		"red", 				xRED			,0},
/* 16 PNC_GLOWING*/{	"glowing", 			xYELLOW			,0},
/* 17 PNC_MOTTLED*/{	"mottled", 			xLIGHTRED		,0},
/* 18 PNC_BLOBBED*/{	"blobby", 			xBROWN			,0},
/* 19 PNC_PINK*/{		"pink", 			xLIGHTMAGENTA	,0},
/* 20 PNC_MOULDED*/{	"mouldy", 			xLIGHTCYAN		,0},
/* 21 PNC_GRAY*/{		"gray", 			xLIGHTGRAY		,0},
/* 22 PNC_MERCURY*/{	"mercury", 			xLIGHTGRAY		,0},
/* 23 PNC_OILY*/{		"oily", 			xDARKGRAY		,0},
/* 24 PNC_VISCOUS*/{	"viscous", 			xLIGHTCYAN		,0},
/* 25 PNC_DARK_RED*/{	"dark red",			xRED			,0},
/* 26 PNC_LIGHT_RED*/{	"light red",		xLIGHTRED		,0},
/* 27 PNC_DARK_BLUE*/{	"dark blue",		xBLUE			,0},
/* 28 PNC_LIGHT_BLUE*/{	"light blue",		xLIGHTBLUE		,0},
/* 29 PNC_BROWN*/{		"brown",			xBROWN			,0},
/* 30 PNC_LIGHT_GRAY*/{	"light gray",		xLIGHTGRAY		,0},
/* 31 PNC_DARK_GRAY*/{	"dark gray",		xDARKGRAY		,0},
/* 32 PNC_DARK_GREEN*/{	"dark green",		xGREEN			,0},
/* 33 PNC_LIGHT_GREEN*/{"light green",		xLIGHTGREEN		,0},
/* 34 PNC_BEIGE*/		{"beige",			xLIGHTGRAY		,0},
/* 35 PNC_AQUAMARINE*/	{"aquamarine",		xCYAN			,0},
/* 36 PNC_CORAL*/		{"coral",			xGREEN			,0},
/* 37 PNC_IVORY*/		{"ivory",			xYELLOW			,0},
/* 38 PNC_MAROON*/		{"maroon",			xRED			,0},
/* 39 PNC_TAN*/			{"tan",				xBROWN			,0},
/* 40 PNC_TURQUOISE*/	{"turquoise",		xCYAN			,0},
/* 41 PNC_VIOLET*/		{"violet",			xMAGENTA		,0},
};


POTION_COLOR POTION_REC::SelectColor(POTION_COLOR pnc)
{
	if (pnc == PNC_RANDOM)
	{
		int count = 1000;
		while (count-- > 0)
		{
			int rp = vRand() % PNC_RANDOM;
			if (pnc_table[rp].is_used == 0)
			{
				pnc_table[rp].is_used = 1;
				return (POTION_COLOR)rp;
			}
		}
		assert(0);
		return PNC_CLEAR;
	} else
	{
		assert(pnc_table[pnc].is_used == 0);
		pnc_table[pnc].is_used = 1;
		return pnc;
	}
}

POTION_REC potion_descr[] = {
{PN_WATER, 				"water",				E_NONE,					100,	1,	1,	POTION_REC::SelectColor(PNC_CLEAR),	0},
{PN_APPLEJUCE, 			"apple juice",			E_NONE,					95,		1,	2,	POTION_REC::SelectColor(PNC_YELLOW),	0},
{PN_ORANGEJUCE,			"orange juice",			E_NONE,					95,		1,	3,	POTION_REC::SelectColor(PNC_ORANGE),	0},
{PN_HEALING,			"healing",				E_HEAL,					10,		4,	200,POTION_REC::SelectColor(PNC_WHITE),	0},
{PN_CURE_LIGHT_WOUNDS,	"cure light wounds",	E_CURE_LIGHT_WOUNDS,	80,		2,	15,	POTION_REC::SelectColor(),	0},
{PN_CURE_SERIOUS_WOUNDS,"cure serious wounds",	E_CURE_SERIOUS_WOUNDS,	70,		2,	40,	POTION_REC::SelectColor(),	0},
{PN_CURE_CRITICAL_WOUNDS,"cure critical wounds",E_CURE_CRITICAL_WOUNDS,	40,		3,	60,	POTION_REC::SelectColor(),	0},
{PN_CURE_MORTAL_WOUNDS,	"cure mortal wounds",	E_CURE_MORTAL_WOUNDS,	20,		3,	100,POTION_REC::SelectColor(),	0},
{PN_POWER,				"power",				E_POWER,				80,		2,	15,	POTION_REC::SelectColor(),	0},
{PN_RESTORATION,		"restoration",			E_RESTORATION,			5,		5,	400,POTION_REC::SelectColor(),	0},
{PN_GAIN_STRENGTH,		"strength",				E_NONE,					10,		4,	1000,POTION_REC::SelectColor(),	0},
{PN_GAIN_WILLPOWER,		"willpower",			E_NONE,					10,		4,	1000,POTION_REC::SelectColor(),	0},
{PN_GAIN_MANA,			"mana",					E_NONE,					10,		4,	1000,POTION_REC::SelectColor(),	0},
{PN_GAIN_TOUGHNESS,		"toughness",			E_NONE,					10,		4,	1000,POTION_REC::SelectColor(),	0},
{PN_GAIN_DEXTERITY,		"swiftness",			E_NONE,					10,		4,	1000,POTION_REC::SelectColor(),	0},
{PN_POISON,				"poison",				E_NONE,					150,	1,	5,	POTION_REC::SelectColor(),	0},
{PN_CURE_POISON,		"cure poison",			E_CURE_POISON,			80,		3,	25, POTION_REC::SelectColor(),	0},
{PN_BLEEDNESS,			"bleeding",				E_NONE,					300,	1,	1,  POTION_REC::SelectColor(),	0},
{PN_DISEASE,			"disease",				E_NONE,					200,	1,	1,  POTION_REC::SelectColor(),	0},
{PN_CURE_DISEASE,		"cure disease",			E_CURE_DISEASE,			50,		3,	50, POTION_REC::SelectColor(),	0},
{PN_HEROISM,			"heroism",				E_HEROISM,				75,		2,	20, POTION_REC::SelectColor(),	0},
{PN_SEE_INVISIBLE,		"see invisible",		E_SEE_INVISIBLE,		30,		3,	30,	POTION_REC::SelectColor(),	0},
{PN_WEAKNESS,			"weakness",				E_NONE,					70,		1,	5,	POTION_REC::SelectColor(),	0},
{PN_CLUMSINESS,			"clumsiness",			E_NONE,					70,		1,	5,	POTION_REC::SelectColor(),	0},
{PN_DEATH,				"death",				E_NONE,					1,		2,	5,	POTION_REC::SelectColor(),	0},
{PN_SATIATION,			"satiation",			E_NONE,					50,		2,	15,	POTION_REC::SelectColor(),	0},
{PN_STARVATION,			"starvation",			E_NONE,					40,		3,	15,	POTION_REC::SelectColor(),	0},
{PN_BOOST_SPEED,		"boost speed",			E_NONE,					30,		3,	100,POTION_REC::SelectColor(),	0},
{PN_SLOWNESS,			"slowness",				E_NONE,					150,	1,	2,	POTION_REC::SelectColor(),	0},
{PN_ACID_RESISTANCE,	"acid resistance",		E_ACID_RESISTANCE,		35,		3,	70,	POTION_REC::SelectColor(),	0},
{PN_FIRE_RESISTANCE,	"fire resistance",		E_FIRE_RESISTANCE,		45,		2,	50,	POTION_REC::SelectColor(),	0},
{PN_COLD_RESISTANCE,	"cold resistance",		E_COLD_RESISTANCE,		45,		2,	50,	POTION_REC::SelectColor(),	0},
{PN_POISON_RESISTANCE,	"poison resistance",	E_POISON_RESISTANCE,	40,		3,	50,	POTION_REC::SelectColor(),	0},
};

int POTION_REC::potion_total_value = 0;
void POTION_REC::RunOnce()
{
	for (int i = 0; i < PN_RANDOM; i++)
	{
		potion_total_value += potion_descr[i].rarity;
	}
}
struct POTION_RUN_ONCE
{
	POTION_RUN_ONCE() {POTION_REC::RunOnce();}
} _POTION_RUN_ONCE;

void POTION_REC::Store(XFile * f)
{
	f->Write(&identify, sizeof(identify));
	f->Write(&force_color, sizeof(POTION_COLOR));
}

void POTION_REC::Restore(XFile * f)
{
	f->Read(&identify, sizeof(identify));
	f->Read(&force_color, sizeof(POTION_COLOR));
}

POTION_NAME POTION_REC::GetRandomPotion()
{
	int val = vRand(potion_total_value);
	int pos = -1;
	do
	{
		pos++;
		val -= potion_descr[pos].rarity;
	} while (val >= 0);
	return (POTION_NAME)pos;
}

POTION_REC * POTION_REC::GetRec(POTION_NAME pn)
{
	for (int i = 0; i < PN_RANDOM; i++)
		if (potion_descr[i].pn == pn)
			return &potion_descr[i];

	return NULL;
}


XPotion::XPotion(POTION_NAME _pn)
{
	if (_pn == PN_RANDOM)
		pn = POTION_REC::GetRandomPotion();
	else
		pn = _pn;

	pdescr = NULL;
	for (int i = 0; i < PN_RANDOM; i++)
		if (potion_descr[i].pn == pn)
		{
			pdescr = &potion_descr[i];
			break;
		}
	assert(pdescr);

	im = IM_POTION;
	bp = BP_OTHER;
	it = IT_POTION;
	view = '!';
	color =	pnc_table[pdescr->force_color].color;

	strcpy(name, pdescr->name);
	
	weight = 3;
	value = pdescr->value;
	dice.Setup("1d2");
}

XPotion::XPotion(XPotion * copy) : XItem((XItem *)copy)
{
	pn = copy->pn;
	pdescr = copy->pdescr;
}

int XPotion::Compare(XObject * o)
{
	assert(dynamic_cast<XPotion *>(o));
	XPotion * pot = (XPotion*)o;
	if (pot->x == x && pot->y == y && pot->pn == pn)
		return 0;
	else
	{
		if (pn > pot->pn)
			return -1;
		else
			return 1;
	}
}

void XPotion::toString(char * buf)
{
	if (isIdentifed())
	{
		if (quantity == 1)
		{
			sprintf(buf, "potion of %s", name);
		}
		else
			sprintf(buf, "heap of %d potions of %s", quantity, name);
	}
	else
	{
		if (quantity == 1)
			sprintf(buf, "%s potion", pnc_table[pdescr->force_color].name);
		else
			sprintf(buf, "heap of %d %s potions", quantity, pnc_table[pdescr->force_color].name);
	}
}

int XPotion::isIdentifed()
{
	return pdescr->identify;
}

void XPotion::Identify(int level)
{
	pdescr->identify = level;
}

int XPotion::onDrink(XCreature * cr)
{
	if (cr->isHero())
	{
		msgwin.Add("You drink a ");
		char buf[256];
		toString(buf);
		strcat(buf, ".");
		msgwin.Add(buf);
	}
	else if (cr->isVisible())
	{
		msgwin.Add(cr->name);
		msgwin.Add("drinks a ");
		char buf[256];
		toString(buf);
		strcat(buf, ".");
		msgwin.Add(buf);
	}

	int flag;

	if (pdescr->effect > E_NONE)
	{
		flag = XEffect::Make(cr, pdescr->effect, 30);
	} else
	{
		switch (pn)
		{
			case PN_WATER:
			case PN_APPLEJUCE:
			case PN_ORANGEJUCE:
				if (cr->isHero())
				{
					msgwin.Add("You feel less thirsty.");
				}
				else if (cr->isVisible())
				{
					msgwin.Add(cr->name);
					msgwin.Add("looks less thirsty.");
				}
				flag = 1;
			break;

			case PN_GAIN_STRENGTH:
				cr->GainAttr(S_STR, 1);
			break;

			case PN_GAIN_TOUGHNESS:
				cr->GainAttr(S_TOU, 1);
			break;

			case PN_GAIN_WILLPOWER:
				cr->GainAttr(S_WIL, 1);
			break;

			case PN_GAIN_DEXTERITY:
				cr->GainAttr(S_DEX, 1);
			break;

			case PN_GAIN_MANA:
				cr->GainAttr(S_MAN, 1);
			break;

			case PN_WEAKNESS:
				cr->GainAttr(S_STR, -1);
			break;

			case PN_CLUMSINESS:
				cr->GainAttr(S_DEX, -1);
			break;

			case PN_DEATH:
				// A potion of death should hurt really badly!
				// As potion of lifelessness, it was just another
				// clumsiness potion, but now it is a potion of death.
				// Moral: Watch what you drink...  This will kill *anyone*.

				// Note, this potion is going to be extremely rare as well.
				if (cr->isHero())
				{
					// Inform the hero of their fate.
					msgwin.Add("You feel your life draining away very rapidly!");
				}
				else if (cr->isVisible())
				{
					if(cr->creature_name > CN_UNIQUE)
					{
						// Uniques are too smart to be fooled by such petty implements...
						msgwin.Add(cr->name);
						msgwin.Add("seems to change");
						switch(cr->creature_person_type)
						{
							case CPT_NAMED_HE:
							case CPT_HE:
								msgwin.Add("his");
							case CPT_NAMED_SHE:
							case CPT_SHE:
								msgwin.Add("her");
							case CPT_NAMED_IT:
							case CPT_IT:
								msgwin.Add("its");
						}
						msgwin.Add("mind and throws the potion away!");
						flag = 1;
						break;
					}
					else
					{
						// Ha ha!  A stupid monster drank the potion of death!
						msgwin.Add(cr->name);
						msgwin.Add("seems to be dying!");
					}
				}
				flag = 1;
				cr->GainAttr(S_STR, -1); // Weakness
				cr->GainAttr(S_DEX, -1); // Damage
				cr->GainAttr(S_TOU, -1); // Fatigue
				cr->GainAttr(S_LEN, -1); // Can't learn if you're dead
				cr->GainAttr(S_WIL, -1); // Lost the will to live
				cr->GainAttr(S_MAN, -1); // Out of touch with nature
				cr->GainAttr(S_PER, -1); // Senses are useless when dead
				cr->GainAttr(S_CHR, -1); // Rotting is ugly
				cr->md->Add(MOD_WOUND,100,cr); // Ensure death
			break;

			case PN_SATIATION:
				cr->nutrio += cr->base_nutrio * 7;
				if (cr->isHero())
				{
					msgwin.Add("You feel much fuller!");
				}
				else if (cr->isVisible())
				{
					msgwin.Add(cr->name);
					msgwin.Add("looks full!");
				}
				flag = 1;
			break;

			case PN_STARVATION:
				cr->nutrio = cr->base_nutrio * 3;
				if (cr->isHero())
				{
					msgwin.Add("You feel hungrier!");
				}
				else if (cr->isVisible())
				{
					msgwin.Add(cr->name);
					msgwin.Add("looks very hungry!");
				}
				flag = 1;
			break;

			case PN_BOOST_SPEED:
				cr->md->Add(MOD_BOOST_SPEED, 100, cr);
				if (cr->isVisible() && !cr->isHero())
				{
					msgwin.Add("moves more quickly!");
				}
				flag = 1;
			break;

			case PN_SLOWNESS:
				cr->md->Add(MOD_SLOWNESS, 100, cr);
				if (cr->isVisible() && !cr->isHero())
				{
					msgwin.Add(cr->name);
					msgwin.Add("moves slowly!");
				}
				flag = 1;
			break;


			case PN_BLEEDNESS:
				cr->md->Add(MOD_WOUND, 30, cr);
				if (cr->isHero())
				{
					msgwin.Add("You begin to bleed.");
				}
				else if (cr->isVisible())
				{
					msgwin.Add(cr->name);
					msgwin.Add("starts to bleed.");
				}
				flag = 1;
			break;

			case PN_DISEASE:
				cr->md->Add(MOD_DISEASE, 25, cr);
				if (cr->isVisible() && !cr->isHero())
				{
					msgwin.Add(cr->name);
					msgwin.Add("looks ill.");
				}
				flag = 1;
			break;

			case PN_POISON:
				cr->md->Add(MOD_POISON, 10, cr);
				if (cr->isVisible() && !cr->isHero())
				{
					msgwin.Add(cr->name);
					msgwin.Add("is poisoned.");
				}
				flag = 1;
			break;


			default: assert(0);
		}
	}
	
	if (flag == 0 && cr->isVisible())
	{
		if (cr->isHero())
		{
			msgwin.Add("You feel nothing special!");
		}
		else
		{
			msgwin.Add("Nothing special happens to ");
			msgwin.Add(cr->name);
			msgwin.Add(".");
		}
	}
	else if (!isIdentifed() && cr->isHero())
	{
		char buf[256];
		Identify(1);
		msgwin.Add("It was");
		toString(buf);
		strcat(buf, ".");
		msgwin.Add(buf);
	}
	return 0; 
}

void XPotion::Store(XFile * f)
{
	XItem::Store(f);
	f->Write(&pn, sizeof(POTION_NAME));
}

void XPotion::Restore(XFile * f)
{
	XItem::Restore(f);
	f->Read(&pn, sizeof(POTION_NAME));

	pdescr = NULL;
	for (int i = 0; i < PN_RANDOM; i++)
		if (potion_descr[i].pn == pn)
		{
			pdescr = &potion_descr[i];
			break;
		}
	assert(pdescr);
}

void XPotion::StoreTable(XFile * f)
{
	for (int i = 0; i < PN_RANDOM; i++)
		potion_descr[i].Store(f);
}

void XPotion::RestoreTable(XFile * f)
{
	for (int i = 0; i < PN_RANDOM; i++)
		potion_descr[i].Restore(f);
}





REGISTER_CLASS(XAlchemyRec);
XAlchemy alchemy;



XAlchemy::XAlchemy()
{
}

XAlchemy::~XAlchemy()
{
}

void XAlchemy::Init()
{
	for (int i = 1; i < 5; i++)
		alchemy.BuildReception(i);
	FILE * f = fopen(vMakePath(HOME_DIR, "recipies.txt"), "w");
	XList<XAlchemyRec *>::iterator it = alchemy.reception.begin();
	while (it != alchemy.reception.end())
	{
		char * c1 = potion_descr[it->pn1].name;
		char * c2 = potion_descr[it->pn2].name;
		char * c3 = potion_descr[it->result].name;
		fprintf(f, "%s + %s = %s\n", c1, c2, c3);
		it++;
	}
	fclose(f);
}

void XAlchemy::GetReceptionName(char * buf, POTION_NAME pn1, POTION_NAME pn2, POTION_NAME pn3)
{
	char * c1 = potion_descr[pn1].name;
	char * c2 = potion_descr[pn2].name;
	char * c3 = potion_descr[pn3].name;
	sprintf(buf, "potion of %s + potion of %s = potion of %s", c1, c2, c3);
}

void XAlchemy::BuildReception(int al_lvl)
{
	POTION_NAME * pTableSrc = NULL;
	int tbl_src = GetPotionCount(al_lvl, &pTableSrc);
	
	POTION_NAME * pTableDest = NULL;
	int tbl_dest = GetPotionCount(al_lvl + 1, &pTableDest);

	int * tbl = new int[tbl_src * tbl_src];
	memset(tbl, -1, sizeof(int) * tbl_src * tbl_src);

	for (int j = 0; j < tbl_dest; j++)
	{
		while (1)
		{
			int pos1 = vRand(tbl_src);
			int pos2 = vRand(tbl_src);
			if (pos1 != pos2 && tbl[tbl_src * pos1 + pos2] == -1)
			{
				tbl[tbl_src * pos1 + pos2] = j;
				XAlchemyRec * alrec = new XAlchemyRec(pTableSrc[pos1], pTableSrc[pos2], pTableDest[j]);
				reception.Add(alrec);
				break;
			}
		}
	}
	delete[] tbl;
	delete[] pTableSrc;
	delete[] pTableDest;
}

int XAlchemy::GetPotionCount(int al_lvl, POTION_NAME ** pTable)
{
	int res = 0;
	int i;
	for (i = 0; i < PN_RANDOM; i++)
		if (potion_descr[i].alchemy_power == al_lvl)
			res++;
	
	*pTable = new POTION_NAME[res];
	
	int tres = 0;
	for (i = 0; i < PN_RANDOM; i++)
		if (potion_descr[i].alchemy_power == al_lvl)
		{
			(*pTable)[tres] = potion_descr[i].pn;
			tres++;
		}


	return res;
}

int XAlchemy::GetReceptionCount()
{
	return alchemy.reception.size();
}

XAlchemyRec * XAlchemy::GetReception(int num)
{
	XList<XAlchemyRec *>::iterator it = alchemy.reception.begin();	
	while (num > 0 && it != alchemy.reception.end())
	{
		it++;
		num--;
	}
	if (it != alchemy.reception.end())
		return it;
	else
		return NULL;
}

int XAlchemy::isValidReception(POTION_NAME pn1, POTION_NAME pn2, POTION_NAME pn3)
{
	XList<XAlchemyRec *>::iterator it = alchemy.reception.begin();	
	while (it != alchemy.reception.end())
	{
		if (it->pn1 == pn1 && it->pn2 == pn2 && it->result == pn3)
			return 1;
		it++;
	}
	return 0;
}

POTION_NAME XAlchemy::GetPotionName(POTION_NAME pn1, POTION_NAME pn2)
{
	XList<XAlchemyRec *>::iterator it = alchemy.reception.begin();	
	while (it != alchemy.reception.end())
	{
		if (it->pn1 == pn1 && it->pn2 == pn2 || it->pn2 == pn1 && it->pn1 == pn2)
			return it->result;
		it++;
	}
	return PN_UNKNOWN;
}

void XAlchemy::Store(XFile * f)
{
	alchemy.reception.StoreList(f);
}

void XAlchemy::Restore(XFile * f)
{
	alchemy.reception.RestoreList(f);
}







