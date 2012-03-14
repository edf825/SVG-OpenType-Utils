#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <arpa/inet.h>
#include "opentype.h"

#define MAX_SIZE 1 << 20
#define TABLE_POS(X) (font + sizeof(Head) + (X) * sizeof(TableHead))

char font[2 * MAX_SIZE];
char svg[MAX_SIZE];

int fontLen;
int svgLen;

uint32_t calcChecksum(char * start, uint32_t length) {
    uint32_t * end = (uint32_t *)(start + ((length + 3) & ~3));

    uint32_t sum = 0;
    uint32_t * iter = (uint32_t *)start;
    for (; iter < end; iter++) {
        sum += htonl(*iter);
    }
    return htonl(sum);
}

int main(int argc, char** argv) {
	
	if (argc < 4) {
		fprintf(stderr, "Too few arguments.\n\t%s <opentype file> <svg file> <output file>\n\n", argv[0]);
		return 1;
	}
	
	FILE * fontFile = fopen(argv[1], "rw");
	fontLen = fread(font, 1, MAX_SIZE, fontFile);

	FILE * svgFile = fopen(argv[2], "r");
	svgLen = fread(svg, 1, MAX_SIZE, svgFile);

	printf("Read %d font bytes; %d svg bytes\n", fontLen, svgLen);

	int numTables = htons(((Head*)font)->numTables);
	printf("Found %d tables\n", numTables);

	// Move everything over to make room for the new head
	fontLen += sizeof(TableHead);
	for (int i = fontLen; i > sizeof(Head) + numTables * sizeof(TableHead); i--) {
		font[i] = font[i - sizeof(TableHead)];
	}

	// Update headers to reflect new offsets
	for (int i = 0; i < numTables; i++) {
		TableHead * head = (TableHead*)TABLE_POS(i);
		printf("Found table %c%c%c%c; length %d; pos %d\n", head->tag[0], head->tag[1], head->tag[2], head->tag[3], htonl(head->length), htonl(head->offset));
		head->offset = htonl(htonl(head->offset) + sizeof(TableHead));
	}

	//TableHead * newHead = (TableHead*)&font[sizeof(Head) + numTables * sizeof(TableHead)];
    TableHead * newHead = new TableHead;
	newHead->tag[0] = 'S';
	newHead->tag[1] = 'V';
	newHead->tag[2] = 'G';
	newHead->tag[3] = ' ';
	newHead->length = htonl(svgLen);
	newHead->offset = htonl(fontLen);
    printf("svg len = %d ; %X ; %X\n", svgLen, svgLen, htonl(svgLen));
    printf("font len = %d ; %X ; %X\n", fontLen, fontLen, htonl(fontLen));

	int svgLenRounded = (svgLen + 7) & ~3;

	// Pad SVG to 4 byte widths
	for (int i = svgLen; i < svgLenRounded; i++) {
		svg[i] = 0;
	}

	// Copy SVG to font
	for (int i = 0; i < svgLenRounded; i++) {
		font[fontLen + i] = svg[i];
	}

	newHead->checksum = calcChecksum(font + fontLen, svgLen);

    // Tables must be sorted by tag as interpreted as a big endian uint32_t
    uint32_t tagLong = htonl(*(uint32_t*)newHead);
    int nextTable = 0;
    for (; nextTable < numTables; nextTable++) {
        char * curTable = TABLE_POS(nextTable);
        if (htonl(*(uint32_t*)curTable) > tagLong) {
            break;
        }
    }

    if (nextTable < numTables) {
        memmove(TABLE_POS(nextTable + 1), TABLE_POS(nextTable), sizeof(TableHead) * (numTables - nextTable));
    }

    memcpy(TABLE_POS(nextTable), newHead, sizeof(TableHead));

    // Update header to expect new table
    ((Head*)font)->numTables = htons(htons(((Head*)font)->numTables) + 1);
    ((Head*)font)->rangeShift = htons(htons(((Head*)font)->rangeShift) + 16);


	FILE * outFile = fopen(argv[3], "w");
	int outLen = fwrite(font, 1, fontLen + svgLenRounded, outFile);

	printf("Wrote %d bytes\n", outLen);

	return 0;
}
