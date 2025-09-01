using System;
using System.Linq;

namespace LeopardCommandTool.Protocol
{
	public static class ProtocolUtils
	{
		public static byte[] BuildCommand(char id, char command)
		{
			byte[] packet = new byte[] { (byte)'0', (byte)id, (byte)command };
			ushort crc = CalcCrc16(packet);
			byte[] crcBytes = BitConverter.GetBytes(crc).Reverse().ToArray();
			byte[] result = new byte[packet.Length + crcBytes.Length + 1];
			Buffer.BlockCopy(packet, 0, result, 0, packet.Length);
			Buffer.BlockCopy(crcBytes, 0, result, packet.Length, crcBytes.Length);
			result[^1] = 0x0D;
			return result;
		}

		public static ushort CalcCrc16(byte[] data)
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

		public static byte[] BuildOpcodeCommand(
			ushort pabPortSerialNumber,
			byte[] leopardSequence,
			ushort opCode = 1,
			ushort sequenceNumber = 0,
			uint timestamp = 0,
			uint leopardSequenceNumber = 0)
		{
			byte[] command = new byte[] {
				(byte)'S', (byte)'K', 0, 0, 0, 0, 0, 0
			}.Concat(BitConverter.GetBytes(sequenceNumber))
			 .Concat(BitConverter.GetBytes(opCode))
			 .Concat(BitConverter.GetBytes(pabPortSerialNumber))
			 .Concat(BitConverter.GetBytes(timestamp))
			 .Concat(BitConverter.GetBytes(leopardSequenceNumber))
			 .Concat(leopardSequence)
			 .ToArray();

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
	}
}

