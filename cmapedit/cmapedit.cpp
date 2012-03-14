#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <list>

using namespace std;

#define MAX_SIZE 2000000
#define TAG_EQUAL(a,b) ((a)[0] == (b)[0] && (a)[1] == (b)[1]\
		&& (a)[2] == (b)[2] && (a)[3] == (b)[3])

struct Head {
	uint32_t ver;
	uint16_t numTables;
	uint16_t searchRange;
	uint16_t entrySelector;
	uint16_t rangeShift;
};

struct TableHead {
	char tag[4];
	uint32_t checksum;
	uint32_t offset;
	uint32_t length;
};

struct CmapHead {
	uint16_t version;
	uint16_t numTables;
};

struct CmapRecord {
	uint16_t platformId;
	uint16_t encodingId;
	uint32_t offset;
};

struct CmapSubtable {
	CmapRecord * head;
	char * table;
};

struct Format4HalfTable {
	uint16_t format;
	uint16_t length;
	uint16_t language;
	uint16_t segCount2;
	uint16_t searchRange;
	uint16_t entrySelector;
	uint16_t rangeShift;
};

struct Format6HalfTable {
	uint16_t format;
	uint16_t length;
	uint16_t language;
	uint16_t firstCode;
	uint16_t entryCount;
};


char font[MAX_SIZE];
int fontLen;

char * cmapStart;


TableHead * findTable(char * name) {
	Head * head = (Head*)font;

	TableHead * found = NULL;
	for (int i = 0; i < htons(head->numTables); i++) {
		TableHead * cur = (TableHead*)&font[sizeof(Head) + i * sizeof(TableHead)];
		if (TAG_EQUAL(cur->tag, name)) {
			found = cur;
		}
	}

	return found;
}


void loadFont(char * filename) {
	FILE * fontFile = fopen(filename, "r");
	fontLen = fread(font, 1, MAX_SIZE, fontFile);

	printf("Read %d bytes\n", fontLen);

	Head * head = (Head*)font;

	TableHead * thead = findTable("cmap");

	cmapStart = font + htonl(thead->offset);
}


list<CmapSubtable> getCmapSubtables() {
	list<CmapSubtable> tables;

	CmapHead * head = (CmapHead*)cmapStart;

	printf("Found %d cmap tables:\n", htons(head->numTables));

	for (int i = 0; i < htons(head->numTables); i++) {
		CmapRecord * record = (CmapRecord*)(cmapStart + sizeof(CmapHead) + i * sizeof(CmapRecord));
		CmapSubtable table = (CmapSubtable) {
			record,
			cmapStart + htonl(record->offset)
		};

		tables.push_back(table);

		printf("\t%.2d:%.2d format %d at %X\n", htons(record->platformId), htons(record->encodingId), htons(*(uint16_t*)table.table), table.table);
	}

	return tables;
}


uint16_t mappings[65536];


void printFormat4Mappings(char * table) {
	Format4HalfTable * head = (Format4HalfTable*)table;
	uint16_t segCount = htons(head->segCount2) / 2;

	char * secondHalf = table + sizeof(Format4HalfTable);
	
	uint16_t * endCount = (uint16_t*)secondHalf;
	uint16_t * startCount = (uint16_t*)secondHalf + segCount + 1;
	int16_t * idDelta = (int16_t*)secondHalf + 2 * segCount + 1;
	uint16_t * idRangeOffset = (uint16_t*)secondHalf + 3 * segCount + 2;
	uint16_t * glyphIdArray = (uint16_t*)secondHalf + 4 * segCount + 2;

	for (int i = 0; i < htons(head->segCount2) / 2; i++) {
		uint16_t start = htons(startCount[i]);
		uint16_t end = htons(endCount[i]);
		uint16_t delta = htons(idDelta[i]);
		printf("%5d to %5d => %5d to %5d\n", start, end, (uint16_t)(start + delta), (uint16_t)(end + delta));
		for (int j = start; j < end; j++) {
			mappings[j] = j + delta;
		}
	}
}


void printFormat6Mappings(char * table) {
	Format6HalfTable * head = (Format6HalfTable*)table;

	uint16_t firstCode = htons(head->firstCode);
	uint16_t * glyphIdArray = (uint16_t*)(table + sizeof(Format6HalfTable));

	for (int i = 0; i < htons(head->length); i++) {
		printf("0x%.8X %5d => %5d\n", (char*)&glyphIdArray[i] - font, i + firstCode, htons(glyphIdArray[i]));
		mappings[firstCode + i] = htons(glyphIdArray[i]);
	}
}


void listMappings(list<CmapSubtable> subtables) {

	for (list<CmapSubtable>::iterator iter = subtables.begin(); iter != subtables.end(); iter++) {
		uint16_t format = htons(*(uint16_t*)iter->table);

		switch (htons(*(uint16_t*)iter->table)) {
			case 4:
				printFormat4Mappings(iter->table);
				break;
			case 6:
				printFormat6Mappings(iter->table);
				break;
			default:
				printf("Unsupported format %d\n", format);
				break;
		}
	}

}


void checksumLoca() {
	TableHead * loca = findTable("loca");

	uint32_t sum = 0;
	for (int i = 0; i < ((htonl(loca->length) + 3) & ~3); i += 4) {
		sum += (*(uint32_t*)&font[htonl(loca->offset) + i]);
	}
	loca->checksum = htonl(sum);
}


void saveFont(char * filename) {
	checksumLoca();
	FILE * fd = fopen(filename, "w");
	if (fwrite(font, 1, fontLen, fd) == fontLen) {
		printf("Wrote font to %s\n", filename);
	} else {
		printf("Writing failed\n");
	}
	fclose(fd);
}


void deleteGlyph(int code) {
	int glyphId = mappings[code];

	TableHead * head = findTable("head");
	uint16_t indexToLocFormat = htons(*(uint16_t*)(font + htonl(head->offset) + 50));

	TableHead * loca = findTable("loca");

	void * addr;

	if (indexToLocFormat == 0) {	// short glyph indices
		uint16_t * locTable = (uint16_t*)(font + htonl(loca->offset));
		locTable[glyphId] = locTable[glyphId + 1];
		addr = &locTable[glyphId];
	} else {	// long glyph indices
		uint32_t * locTable = (uint32_t*)(font + htonl(loca->offset));
		locTable[glyphId] = locTable[glyphId + 1];
		addr = &locTable[glyphId];
	}

	printf("Removed glyph for char code %d, glyph id %d, address %X\n", code, glyphId, (char*)addr - font);
}


int main (int argc, char ** argv) {

	if (argc < 2) {
		fprintf(stderr, "Usage: %s <opentype font file>\n", argv[0]);
	}

	loadFont(argv[1]);

	list<CmapSubtable> subtables = getCmapSubtables();

	listMappings(subtables);

	printf("\ts <filename>\tsave\n");
	printf("\td <char num>\tdelete glyph\n");
	printf("\tm <char num>\tlookup glyph by number\n");
	printf("\tc <char>\t lookup glyph by character\n");
	printf("\tq\tquit\n");

	char com;
	int code;
	char str[64];
	while (true) {
		scanf("%c", &com);

		switch(com) {
			case 's':	// Save
			case 'S':
				scanf("%s", str);
				saveFont(str);
				break;
			case 'd': // Delete glyph
			case 'D':
				scanf("%d", &code);
				deleteGlyph(code);
				break;
			case 'm':	// Lookup glyph by number
			case 'M':
				scanf("%d", &code);
				printf("Character #%d maps to %d\n", code, mappings[code]);
				break;
			case 'c':	// Lookup glyph by character
			case 'C':
				scanf("%s", str);
				printf("Character '%c' (%d) maps to %d\n", str[0], str[0], mappings[str[0]]);
				break;
			case 'q':
			case 'Q':
				exit(0);
		}

		scanf("\n");
	}

	return 0;
}
