using System;

namespace LeopardCommandTool
{
	public static class PacketBuilder
	{
		public static byte[] BuildCommand(char ID, char command)
		{
			byte[] packet = new byte[] { (byte)'0', (byte)ID, (byte)command };
			ushort crc = CalcCRC16(packet);
			byte[] crcBytes = BitConverter.GetBytes(crc);
			Array.Reverse(crcBytes); // big-endian in output
			byte[] result = new byte[packet.Length + crcBytes.Length + 1];
			Buffer.BlockCopy(packet, 0, result, 0, packet.Length);
			Buffer.BlockCopy(crcBytes, 0, result, packet.Length, crcBytes.Length);
			result[result.Length - 1] = 0x0D; // CR
			return result;
		}

		public static ushort CalcCRC16(byte[] data)
		{
			ushort cs = 0;
			foreach (byte b in data)
			{
				cs ^= (ushort)(b << 8);
				for (int i = 0; i < 8; i++)
				{
					ushort carry = (ushort)(cs & 0x8000);
					if (carry != 0)
					{
						carry = 1;
						cs ^= 0x8810;
					}
					cs = (ushort)((cs << 1) + carry);
				}
			}
			return cs;
		}

		public static byte[] BuildOpcodeCommand(ushort pabPortSerialNumber, byte[] leopardSequence,
			ushort opCode = 1, ushort sequenceNumber = 0, uint timestamp = 0, uint leopardSequenceNumber = 0)
		{
			byte[] command = new byte[] { (byte)'S', (byte)'K', 0, 0, 0, 0, 0, 0 };
			command = Combine(
				command,
				BitConverter.GetBytes(sequenceNumber),
				BitConverter.GetBytes(opCode),
				BitConverter.GetBytes(pabPortSerialNumber),
				BitConverter.GetBytes(timestamp),
				BitConverter.GetBytes(leopardSequenceNumber),
				leopardSequence
			);

			ushort length = (ushort)command.Length;
			command[2] = (byte)(length & 0xFF);
			command[3] = (byte)((length >> 8) & 0xFF);

			ushort checksum = CalculateChecksum(command);
			command[6] = (byte)(checksum & 0xFF);
			command[7] = (byte)((checksum >> 8) & 0xFF);

			return command;
		}

		public static ushort CalculateChecksum(byte[] data)
		{
			int sum = 0;
			for (int i = 0; i < data.Length; i++)
			{
				sum += data[i];
			}
			return (ushort)(~sum);
		}

		public static byte[] ToBigEndianBytes(ushort value)
		{
			byte[] b = BitConverter.GetBytes(value);
			Array.Reverse(b);
			return b;
		}

		private static byte[] Combine(params byte[][] arrays)
		{
			int total = 0;
			for (int i = 0; i < arrays.Length; i++)
			{
				total += arrays[i].Length;
			}
			byte[] result = new byte[total];
			int offset = 0;
			for (int i = 0; i < arrays.Length; i++)
			{
				Buffer.BlockCopy(arrays[i], 0, result, offset, arrays[i].Length);
				offset += arrays[i].Length;
			}
			return result;
		}
	}
}

