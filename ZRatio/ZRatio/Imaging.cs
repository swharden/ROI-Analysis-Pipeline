using SciTIF.LUTs;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ZRatio;
public static class Imaging
{
    public static (SciTIF.Image red, SciTIF.Image green) GetProjectionImages(string zStackFolder)
    {
        string[] pathsRed = Directory.GetFiles(zStackFolder, "*_Ch1_*.ome.tif");
        string[] pathsGreen = Directory.GetFiles(zStackFolder, "*_Ch2_*.ome.tif");

        if (!pathsRed.Any())
            throw new InvalidOperationException("no red images found");

        if (!pathsGreen.Any())
            throw new InvalidOperationException("no green images found");

        if (pathsRed.Length != pathsGreen.Length)
            throw new InvalidOperationException("different number of red and green images");

        SciTIF.Image[] imagesRed = pathsRed.Select(x => new SciTIF.TifFile(x).GetImage(0, 0, 0)).ToArray();
        SciTIF.Image projRed = new SciTIF.ImageStack(imagesRed).ProjectMax();

        SciTIF.Image[] imagesGreen = pathsGreen.Select(x => new SciTIF.TifFile(x).GetImage(0, 0, 0)).ToArray();
        SciTIF.Image projGreen = new SciTIF.ImageStack(imagesGreen).ProjectMax();

        return (projRed, projGreen);
    }

    private static SciTIF.Image Copy(this SciTIF.Image source)
    {
        double[] values = new double[source.Values.Length];
        Array.Copy(source.Values, values, source.Values.Length);
        return new SciTIF.Image(source.Width, source.Height, values);
    }

    public static Bitmap GetBitmap(SciTIF.Image red, SciTIF.Image green)
    {
        red = red.Copy();
        green = green.Copy();

        red.AutoScale();
        green.AutoScale();
        SciTIF.ImageRGB rgb = new(red, green, red);
        byte[] bytes = rgb.GetBitmapBytes();

        Bitmap bmp;
        using (MemoryStream ms = new(bytes))
        {
            bmp = new(ms);
        }

        return bmp;
    }

    public static double RoiMean(this SciTIF.Image img, int x1, int x2, int y1, int y2)
    {
        double sum = 0;
        int pixels = (x2 - x1 + 1) * (y2 - y1 + 1);

        for (int x = x1; x <= x2; x++)
        {
            for (int y = y1; y <= y2; y++)
            {
                sum += img.GetPixel(x, y);
            }
        }

        return sum / pixels;
    }
}
