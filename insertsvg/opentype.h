struct Head {
	uint32_t ver;
	short numTables;
	short searchRange;
	short entrySelector;
	short rangeShift;
};

struct TableHead {
	char tag[4];
	uint32_t checksum;
	uint32_t offset;
	uint32_t length;
};

