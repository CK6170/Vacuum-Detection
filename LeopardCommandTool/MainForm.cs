using System;
using System.Text;
using System.Windows.Forms;

namespace LeopardCommandTool
{
	public partial class MainForm : Form
	{
		public MainForm()
		{
			InitializeComponent();
		}

		private void btnBuildOpcode_Click(object sender, EventArgs e)
		{
			if (!HexUtils.TryParseUInt16(txtPabPortSerialNumber.Text, out ushort pabPortSerialNumber, out string? err1))
			{
				MessageBox.Show($"Invalid PAB Port Serial Number: {err1}", "Input Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
				return;
			}

			if (!HexUtils.TryParseHexBytes(txtLeopardSequence.Text, out byte[]? leopardSequence, out string? err2))
			{
				MessageBox.Show($"Invalid Leopard Sequence: {err2}", "Input Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
				return;
			}

			ushort opCode = 1;
			if (!string.IsNullOrWhiteSpace(txtOpCode.Text))
			{
				if (!HexUtils.TryParseUInt16(txtOpCode.Text, out opCode, out string? err3))
				{
					MessageBox.Show($"Invalid OpCode: {err3}", "Input Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
					return;
				}
			}

			ushort sequenceNumber = 0;
			if (!string.IsNullOrWhiteSpace(txtSequenceNumber.Text))
			{
				if (!HexUtils.TryParseUInt16(txtSequenceNumber.Text, out sequenceNumber, out string? err4))
				{
					MessageBox.Show($"Invalid Sequence Number: {err4}", "Input Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
					return;
				}
			}

			uint timestamp = 0;
			if (!string.IsNullOrWhiteSpace(txtTimestamp.Text))
			{
				if (!HexUtils.TryParseUInt32(txtTimestamp.Text, out timestamp, out string? err5))
				{
					MessageBox.Show($"Invalid Timestamp: {err5}", "Input Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
					return;
				}
			}

			uint leopardSequenceNumber = 0;
			if (!string.IsNullOrWhiteSpace(txtLeopardSequenceNumber.Text))
			{
				if (!HexUtils.TryParseUInt32(txtLeopardSequenceNumber.Text, out leopardSequenceNumber, out string? err6))
				{
					MessageBox.Show($"Invalid Leopard Sequence Number: {err6}", "Input Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
					return;
				}
			}

			byte[] command = PacketBuilder.BuildOpcodeCommand(pabPortSerialNumber, leopardSequence, opCode, sequenceNumber, timestamp, leopardSequenceNumber);
			txtOpcodeCommandHex.Text = HexUtils.BytesToHex(command);
		}

		private void btnBuildCrcPacket_Click(object sender, EventArgs e)
		{
			if (!HexUtils.TryParseCharOrByte(txtId.Text, out byte idByte, out string? idErr))
			{
				MessageBox.Show($"Invalid ID: {idErr}", "Input Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
				return;
			}
			if (!HexUtils.TryParseCharOrByte(txtCommand.Text, out byte commandByte, out string? cmdErr))
			{
				MessageBox.Show($"Invalid Command: {cmdErr}", "Input Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
				return;
			}

			byte[] packet = PacketBuilder.BuildCommand((char)idByte, (char)commandByte);
			txtCrcPacketHex.Text = HexUtils.BytesToHex(packet);
			ushort crc = PacketBuilder.CalcCRC16(new byte[] { (byte)'0', idByte, commandByte });
			lblCrcValue.Text = $"CRC16 (big-endian): {HexUtils.BytesToHex(PacketBuilder.ToBigEndianBytes(crc))}";
		}
	}
}

