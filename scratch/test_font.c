#include <stdio.h>
#include <math.h>

int main() {
    // 'T' character bitmap
    unsigned char t_data[8] = {0x7E, 0x7E, 0x18, 0x18, 0x18, 0x18, 0x18, 0x00};
    int CHAR_SIZE = 64;

    for (int Y = 0; Y < CHAR_SIZE; Y += 4) { // Print every 4th line
        for (int X = 0; X < CHAR_SIZE; X += 4) { // Print every 4th char
            float v = (Y + 0.5f) / CHAR_SIZE;
            float py = v * 8.0f - 0.5f;
            float fy0 = floorf(py);
            int y0 = (int)fy0;
            int y1 = y0 + 1;
            float ty = py - fy0;
            if (y0 < 0) { y0 = 0; y1 = 0; }
            if (y1 > 7) { y0 = 7; y1 = 7; }

            float u = (X + 0.5f) / CHAR_SIZE;
            float px = u * 8.0f - 0.5f;
            float fx0 = floorf(px);
            int x0 = (int)fx0;
            int x1 = x0 + 1;
            float tx = px - fx0;
            if (x0 < 0) { x0 = 0; x1 = 0; }
            if (x1 > 7) { x0 = 7; x1 = 7; }

            float v00 = ((t_data[y0] >> (7 - x0)) & 1) ? 1.0f : 0.0f;
            float v10 = ((t_data[y0] >> (7 - x1)) & 1) ? 1.0f : 0.0f;
            float v01 = ((t_data[y1] >> (7 - x0)) & 1) ? 1.0f : 0.0f;
            float v11 = ((t_data[y1] >> (7 - x1)) & 1) ? 1.0f : 0.0f;

            float val = (1.0f - tx) * (1.0f - ty) * v00 +
                        tx * (1.0f - ty) * v10 +
                        (1.0f - tx) * ty * v01 +
                        tx * ty * v11;

            float alpha_f = val * val * (3.0f - 2.0f * val);
            int alpha = (int)(255.0f * alpha_f);
            
            if (alpha == 0) {
                printf(".");
            } else if (alpha == 255) {
                printf("#");
            } else {
                printf("+"); // Semi-transparent pixels
            }
        }
        printf("\n");
    }
    return 0;
}
