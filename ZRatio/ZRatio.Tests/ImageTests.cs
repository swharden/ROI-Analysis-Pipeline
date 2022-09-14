using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ZRatio.Tests;
internal class ImageTests
{
    [Test]
    public void Test_ZProjection()
    {
        (SciTIF.Image red, SciTIF.Image green) = Imaging.GetProjectionImages(SampleData.RatiometricZSeriesFolder);
        Bitmap bmp = Imaging.GetBitmap(red, green);
        bmp.Width.Should().Be(512);
        bmp.Height.Should().Be(512);
    }
}
