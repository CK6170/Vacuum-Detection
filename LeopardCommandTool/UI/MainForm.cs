using System;
using System.Drawing;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace LeopardCommandTool.UI
{
	public partial class MainForm : Form
	{
		public MainForm()
		{
			InitializeComponent();
		}

		private void btnBuildOpcode_Click(object sender, EventArgs e)
		{
			try
			{
				ushort pabPortSerialNumber = ParseUShort(txtPabPortSerialNumber.Text, "pabPortSerialNumber");
				byte[] leopardSequence = ParseHexBytes(txtLeopardSequence.Text);
				ushort opCode = ParseUShortOrDefault(txtOpCode.Text, 1);
				ushort sequenceNumber = ParseUShortOrDefault(txtSequenceNumber.Text, 0);
				uint timestamp = ParseUIntOrDefault(txtTimestamp.Text, 0);
				uint leopardSequenceNumber = ParseUIntOrDefault(txtLeopardSequenceNumber.Text, 0);

				byte[] command = Protocol.ProtocolUtils.BuildOpcodeCommand(
					pabPortSerialNumber,
					leopardSequence,
					opCode,
					sequenceNumber,
					timestamp,
					leopardSequenceNumber);

				txtOutput.Text = ToHex(command);
			}
			catch (Exception ex)
			{
				ShowError(ex.Message);
			}
		}

		private void btnBuildLeopard_Click(object sender, EventArgs e)
		{
			try
			{
				char id = ParseSingleChar(txtLeopardId.Text, "ID");
				char cmd = ParseSingleChar(txtLeopardCommand.Text, "Command");
				byte[] packet = Protocol.ProtocolUtils.BuildCommand(id, cmd);
				txtLeopardCmd.Text = ToHex(packet);
			}
			catch (Exception ex)
			{
				ShowError(ex.Message);
			}
		}

		private void btnCopy_Click(object sender, EventArgs e)
		{
			try
			{
				string all = string.Join("\n\n", new[] { txtOutput.Text, txtLeopardCmd.Text }.Where(s => !string.IsNullOrWhiteSpace(s)));
				if (!string.IsNullOrEmpty(all))
				{
					Clipboard.SetText(all);
				}
			}
			catch (Exception ex)
			{
				ShowError(ex.Message);
			}
		}

		private static ushort ParseUShort(string text, string name)
		{
			if (string.IsNullOrWhiteSpace(text))
				throw new ArgumentException($"{name} is required");
			if (text.StartsWith("0x", StringComparison.OrdinalIgnoreCase))
			{
				return ushort.Parse(text[2..], NumberStyles.HexNumber, CultureInfo.InvariantCulture);
			}
			return ushort.Parse(text, CultureInfo.InvariantCulture);
		}

		private static ushort ParseUShortOrDefault(string text, ushort defaultValue)
		{
			if (string.IsNullOrWhiteSpace(text)) return defaultValue;
			return ParseUShort(text, "value");
		}

		private static uint ParseUIntOrDefault(string text, uint defaultValue)
		{
			if (string.IsNullOrWhiteSpace(text)) return defaultValue;
			if (text.StartsWith("0x", StringComparison.OrdinalIgnoreCase))
			{
				return uint.Parse(text[2..], NumberStyles.HexNumber, CultureInfo.InvariantCulture);
			}
			return uint.Parse(text, CultureInfo.InvariantCulture);
		}

		private static byte[] ParseHexBytes(string hex)
		{
			if (string.IsNullOrWhiteSpace(hex)) throw new ArgumentException("leopardSequence is required");
			string cleaned = new string(hex.Where(c => !char.IsWhiteSpace(c) && c != ',').ToArray());
			if (cleaned.Length % 2 != 0) throw new ArgumentException("Invalid hex length");
			byte[] result = new byte[cleaned.Length / 2];
			for (int i = 0; i < result.Length; i++)
			{
				result[i] = byte.Parse(cleaned.Substring(i * 2, 2), NumberStyles.HexNumber, CultureInfo.InvariantCulture);
			}
			return result;
		}

		private static char ParseSingleChar(string text, string name)
		{
			if (string.IsNullOrEmpty(text) || text.Length != 1)
				throw new ArgumentException($"{name} must be a single ASCII character");
			return text[0];
		}

		private static string ToHex(byte[] data)
		{
			StringBuilder sb = new StringBuilder(data.Length * 3);
			for (int i = 0; i < data.Length; i++)
			{
				if (i > 0) sb.Append(' ');
				sb.Append(data[i].ToString("X2"));
			}
			return sb.ToString();
		}

		private void ShowError(string message)
		{
			MessageBox.Show(this, message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
		}
	}
}

