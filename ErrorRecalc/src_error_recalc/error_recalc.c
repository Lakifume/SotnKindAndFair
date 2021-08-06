#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

// all the difficult code here is stolen from Neill Corlett.
// original source is cdpatch.c from cmdpack.
// also stole this:

//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
////////////////////////////////////////////////////////////////////////////////

int optional_form2_edc_calculated=1;

////////////////////////////////////////////////////////////////////////////////
//
// LUTs for computing ECC/EDC
//
static uint8_t  ecc_f_lut[256];
static uint8_t  ecc_b_lut[256];
static uint32_t edc_lut  [256];

static void eccedc_init(void) {
    uint32_t i, j, edc;
    for(i = 0; i < 256; i++) {
        j = (i << 1) ^ (i & 0x80 ? 0x11D : 0);
        ecc_f_lut[i    ] = (uint8_t)j;
        ecc_b_lut[i ^ j] = (uint8_t)i;
        edc = i;
        for(j = 0; j < 8; j++) {
            edc = (edc >> 1) ^ (edc & 1 ? 0xD8018001 : 0);
        }
        edc_lut[i] = edc;
    }
}

static void set32lsb(uint8_t* p, uint32_t value) {
    p[0] = (uint8_t)(value >>  0);
    p[1] = (uint8_t)(value >>  8);
    p[2] = (uint8_t)(value >> 16);
    p[3] = (uint8_t)(value >> 24);
}

////////////////////////////////////////////////////////////////////////////////
//
// Compute EDC for a block
//
static void edc_computeblock(const uint8_t* src, size_t size, uint8_t* dest) {
    uint32_t edc = 0;
    while(size--) {
        edc = (edc >> 8) ^ edc_lut[(edc ^ (*src++)) & 0xFF];
    }
    set32lsb(dest, edc);
}

////////////////////////////////////////////////////////////////////////////////
//
// Compute ECC for a block (can do either P or Q)
//
static void ecc_computeblock(
    uint8_t* src,
    uint32_t major_count,
    uint32_t minor_count,
    uint32_t major_mult,
    uint32_t minor_inc,
    uint8_t* dest
) {
    uint32_t size = major_count * minor_count;
    uint32_t major, minor;
    for(major = 0; major < major_count; major++) {
        uint32_t index = (major >> 1) * major_mult + (major & 1);
        uint8_t ecc_a = 0;
        uint8_t ecc_b = 0;
        for(minor = 0; minor < minor_count; minor++) {
            uint8_t temp = src[index];
            index += minor_inc;
            if(index >= size) index -= size;
            ecc_a ^= temp;
            ecc_b ^= temp;
            ecc_a = ecc_f_lut[ecc_a];
        }
        ecc_a = ecc_b_lut[ecc_f_lut[ecc_a] ^ ecc_b];
        dest[major              ] = ecc_a;
        dest[major + major_count] = ecc_a ^ ecc_b;
    }
}

//
// Generate ECC P and Q codes for a block
//
static void ecc_generate(uint8_t* sector, int zeroaddress) {
    uint8_t saved_address[4];
    //
    // Save the address and zero it out, if necessary
    //
    if(zeroaddress) {
        memmove(saved_address, sector + 12, 4);
        memset(sector + 12, 0, 4);
    }
    //
    // Compute ECC P code
    //
    ecc_computeblock(sector + 0xC, 86, 24,  2, 86, sector + 0x81C);
    //
    // Compute ECC Q code
    //
    ecc_computeblock(sector + 0xC, 52, 43, 86, 88, sector + 0x8C8);
    //
    // Restore the address, if necessary
    //
    if(zeroaddress) {
        memmove(sector + 12, saved_address, 4);
    }
}


////////////////////////////////////////////////////////////////////////////////
//
// CD sync header
//
static const uint8_t sync_header[12] = {
    0x00,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0x00
};

////////////////////////////////////////////////////////////////////////////////
//
// Generate ECC/EDC information for a sector (must be 2352 = 0x930 bytes)
//
static void eccedc_generate(uint8_t* sector) {
    //
    // Generate sync
    //
    memmove(sector, sync_header, sizeof(sync_header));
    switch(sector[0x0F]) {
    case 0x00:
        //
        // Mode 0: no data; generate zeroes
        //
        memset(sector + 0x10, 0, 0x920);
        break;

    case 0x01:
        //
        // Mode 1:
        //
        // Compute EDC
        //
        edc_computeblock(sector + 0x00, 0x810, sector + 0x810);
        //
        // Zero out reserved area
        //
        memset(sector + 0x814, 0, 8);
        //
        // Generate ECC P/Q codes
        //
        ecc_generate(sector, 0);
        break;

    case 0x02:
        //
        // Mode 2:
        //
        // Make sure XA flags match
        //
        memmove(sector + 0x14, sector + 0x10, 4);

        if(!(sector[0x12] & 0x20)) {
            //
            // Form 1: Compute EDC
            //
            edc_computeblock(sector + 0x10, 0x808, sector + 0x818);
            //
            // Generate ECC P/Q codes
            //
            ecc_generate(sector, 1);

        } else {
            //
            // Form 2: Compute EDC
            //
            if (optional_form2_edc_calculated==0)
            {
              *(uint32_t*)(sector+0x92C)=0;
            }
            else
            {
              edc_computeblock(sector + 0x10, 0x91C, sector + 0x92C);
            }
        }
        break;
    }
}

////////////////////////////////////////////////////////////////////////////////
//
// Returns nonzero if any bytes in the array are nonzero
//
static int anynonzero(const uint8_t* data, size_t len) {
    for(; len; len--) {
        if(*data++) { return 1; }
    }
    return 0;
}

////////////////////////////////////////////////////////////////////////////////
//
// Verify EDC for a sector (must be 2352 = 0x930 bytes)
// Returns 0 on success
//
static int edc_verify(const uint8_t* sector) {
    uint8_t myedc[4];
    //
    // Verify sync
    //
    if(memcmp(sector, sync_header, sizeof(sync_header))) { return 1; }

    switch(sector[0x0F]) {
    case 0x00:
        //
        // Mode 0: no data; everything had better be zero
        //
        return anynonzero(sector + 0x10, 0x920);

    case 0x01:
        //
        // Mode 1
        //
        edc_computeblock(sector + 0x00, 0x810, myedc);
        return memcmp(myedc, sector + 0x810, 4);

    case 0x02:
        //
        // Mode 2: Verify that the XA type is correctly copied twice
        //
        if(memcmp(sector + 0x10, sector + 0x14, 4)) { return 1; }

        if(!(sector[0x12] & 0x20)) {
            //
            // Form 1
            //
            edc_computeblock(sector + 0x10, 0x808, myedc);
            return memcmp(myedc, sector + 0x818, 4);

        } else {
            //
            // Form 2
            //
            edc_computeblock(sector + 0x10, 0x91C, myedc);
            return memcmp(myedc, sector + 0x92C, 4);
        }
    }
    //
    // Invalid mode
    //
    return 1;
}

static int audio_guess(const uint8_t* sector) // 1: looks like audio 0: normal
{
  if
  (
    ( !memcmp(sector,sync_header,sizeof(sync_header)) ) &&
    ( *(sector+0xD)<0x60                              ) &&
    ( *(sector+0xE)<0x75                              ) &&
    ( *(sector+0xF)<3                                 )
  )
  {return 0;}
  return 1;
}

int main(int argc,char* argv[])
{
  eccedc_init();
  if (argc==3) {optional_form2_edc_calculated=((*argv[2])=='0')?0:1;}
  else if (argc!=2) {printf("error: bad args\n");return 0;}
  FILE* fp=fopen(argv[1],"r+b");
  if (fp==NULL) {printf("error: unable to open file\n");return 0;}
  fseek(fp,0,SEEK_END);
  unsigned long fs=ftell(fp);
  if (fs%2352!=0) {printf("error: image not in 2352 byte sectors\n");goto no;}
  rewind(fp);
  uint8_t* file=NULL;
  file=malloc(fs);
  if (file==NULL) {printf("error: memory problem\n");goto no;}
  if (fread(file,fs,1,fp)!=1) {printf("error: cannot read\n");goto no;}
  if (edc_verify(file)!=0) {printf("error: sector 0 not a valid 2352 sector\n");goto no;}
  
  unsigned int sector=16;
  for(;sector<(fs/2352);sector++)
  {
    if (audio_guess(file+sector*2352))
    {
      printf("warning: sector %u looks like an audio sector, will recalculate earlier sectors only\n",sector);
      break;
    }
    eccedc_generate(file+sector*2352);
  }
  
  rewind(fp);
  if (fwrite(file,fs,1,fp)!=1) {printf("error: cannot write\n");}
  no:
  fclose(fp);
}