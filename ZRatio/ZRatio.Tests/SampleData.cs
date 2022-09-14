using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ZRatio.Tests;
internal class SampleData
{
    public static string SampleDataFolder => Path.GetFullPath(Path.Combine(TestContext.CurrentContext.TestDirectory, "../../../../../data"));

    public static string RatiometricZSeriesFolder = Path.Combine(SampleDataFolder, "ZSeries-09092022-1241-1659");

    [Test]
    public void Test_DataFolder_Exists()
    {
        Directory.Exists(SampleDataFolder).Should().BeTrue();
        Directory.Exists(RatiometricZSeriesFolder).Should().BeTrue();
    }
}
