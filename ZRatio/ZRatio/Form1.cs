namespace ZRatio;

public partial class Form1 : Form
{
    PointF RoiCorner1;
    PointF RoiCorner2;
    SciTIF.Image? Red;
    SciTIF.Image? Green;
    System.Windows.Forms.Timer Timer = new() { Enabled = true, Interval = 20 };
    bool RenderRequired;

    public Form1()
    {
        InitializeComponent();
        LoadZFolder(@"C:\Users\scott\Documents\GitHub\ROI-Analysis-Pipeline\data\ZSeries-09092022-1241-1659");
        pictureBox1.MouseDown += PictureBox1_MouseDown;
        pictureBox1.MouseUp += PictureBox1_MouseUp;
        pictureBox1.MouseMove += PictureBox1_MouseMove;
        nudX1.ValueChanged += Nud_ValueChanged;
        nudX2.ValueChanged += Nud_ValueChanged;
        nudY1.ValueChanged += Nud_ValueChanged;
        nudY2.ValueChanged += Nud_ValueChanged;
        Timer.Tick += Timer_Tick;
    }

    private void Nud_ValueChanged(object? sender, EventArgs e)
    {
        RoiCorner1 = new((int)nudX1.Value, (int)nudY1.Value);
        RoiCorner2 = new((int)nudX2.Value, (int)nudY2.Value);
        UpdateEverything();
    }

    private void Timer_Tick(object? sender, EventArgs e)
    {
        if (RenderRequired)
        {
            RenderRequired = false;
            UpdateEverything();
        }
    }

    private void PictureBox1_MouseMove(object? sender, MouseEventArgs e)
    {
        if (e.Button == MouseButtons.Left)
        {
            RoiCorner2 = new(e.X, e.Y);
            RenderRequired = true;
        }
    }

    private void PictureBox1_MouseDown(object? sender, MouseEventArgs e)
    {
        RoiCorner1 = new(e.X, e.Y);
        RoiCorner2 = new(e.X, e.Y);
        RenderRequired = true;
    }

    private void PictureBox1_MouseUp(object? sender, MouseEventArgs e)
    {
        RoiCorner2 = new(e.X, e.Y);
        UpdateEverything();
        UpdateNudValues();
    }

    private void LoadZFolder(string path)
    {
        (Red, Green) = Imaging.GetProjectionImages(path);
        ResetNudValues();
        UpdateEverything();
    }

    private void ResetNudValues()
    {
        if (Red is null || Green is null)
            return;

        nudX1.Value = 0;
        nudX1.Maximum = Red.Width;
        nudX2.Value = 0;
        nudX2.Maximum = Red.Width;
        nudY1.Value = 0;
        nudY1.Maximum = Red.Height;
        nudY2.Value = 0;
        nudY2.Maximum = Red.Height;
    }

    private void UpdateEverything()
    {
        if (Red is null || Green is null)
            return;

        UpdateBitmap();
        UpdateAnalysisText();
    }

    private (int left, int right, int top, int bottom) GetRoiBounds()
    {
        if (Red is null || Green is null)
            throw new InvalidOperationException();

        int left = (int)Math.Min(RoiCorner1.X, RoiCorner2.X);
        int right = (int)Math.Max(RoiCorner1.X, RoiCorner2.X);
        int top = (int)Math.Min(RoiCorner1.Y, RoiCorner2.Y);
        int bottom = (int)Math.Max(RoiCorner1.Y, RoiCorner2.Y);

        left = Math.Max(0, left);
        top = Math.Max(0, top);
        right = Math.Min(Green.Width - 1, right);
        bottom = Math.Min(Green.Height - 1, bottom);

        return (left, right, top, bottom);
    }

    private void UpdateBitmap()
    {
        if (Red is null || Green is null)
            return;

        (int left, int right, int top, int bottom) = GetRoiBounds();

        Bitmap bmp = Imaging.GetBitmap(Red, Green);
        Graphics gfx = Graphics.FromImage(bmp);

        // outline (not inclusive)
        Rectangle rect = new(left - 1, top - 1, right - left + 2, bottom - top + 2);

        gfx.DrawRectangle(Pens.Yellow, rect);

        var oldImage = pictureBox1.Image;
        pictureBox1.Image = bmp;
        oldImage?.Dispose();
    }

    private void UpdateNudValues()
    {
        (int left, int right, int top, int bottom) = GetRoiBounds();

        nudX1.Value = left;
        nudX2.Value = right;
        nudY1.Value = top;
        nudY2.Value = bottom;
    }

    private void UpdateAnalysisText()
    {
        if (Red is null || Green is null)
            return;

        (int left, int right, int top, int bottom) = GetRoiBounds();
        lblWidth.Text = $"Width: {right - left + 1}";
        lblHeight.Text = $"Height: {bottom - top + 1}";

        double greenMean = Green.RoiMean(left, right, top, bottom);
        double redMean = Red.RoiMean(left, right, top, bottom);
        double ratio = greenMean / redMean * 100;
        lblGreen.Text = $"Green: {greenMean:N2}";
        lblRed.Text = $"Red: {redMean:N2}";
        lblRatio.Text = $"Ratio: {ratio:N2}%";
    }
}
