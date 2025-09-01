using System;
using System.Linq;
using System.Text;

namespace CommandBuilder
{
    internal static class Program
    {
        static void Main()
        {
            Console.WriteLine("=== Command Builder Console Application ===");
            Console.WriteLine();

            while (true)
            {
                Console.WriteLine("Choose an option:");
                Console.WriteLine("1. Build Opcode Command");
                Console.WriteLine("2. Generate Leopard Sequence");
                Console.WriteLine("3. Exit");
                Console.Write("Enter choice (1-3): ");

                string choice = Console.ReadLine();

                switch (choice)
                {
                    case "1":
                        BuildOpcodeCommandInteractive();
                        break;
                    case "2":
                        GenerateLeopardSequenceInteractive();
                        break;
                    case "3":
                        return;
                    default:
                        Console.WriteLine("Invalid choice. Please try again.");
                        break;
                }

                Console.WriteLine();
                Console.WriteLine("Press any key to continue...");
                Console.ReadKey();
                Console.Clear();
            }
        }

        static void BuildOpcodeCommandInteractive()
        {
            Console.WriteLine("\n=== Build Opcode Command ===");

            // Required fields
            Console.Write("Enter PAB Port Serial Number: ");
            if (!ushort.TryParse(Console.ReadLine(), out ushort pabPortSerialNumber))
            {
                Console.WriteLine("Invalid PAB Port Serial Number. Using default: 0");
                pabPortSerialNumber = 0;
            }

            Console.Write("Enter Leopard Sequence (hex, e.g., '01 02 03' or '010203'): ");
            string leopardSeqInput = Console.ReadLine();
            byte[] leopardSequence = ParseHexString(leopardSeqInput);
            
            if (leopardSequence.Length == 0)
            {
                Console.WriteLine("Invalid or empty Leopard Sequence. Using default: [0x01, 0x02, 0x03]");
                leopardSequence = new byte[] { 0x01, 0x02, 0x03 };
            }

            // Optional fields
            Console.Write("Enter OpCode (default: 1): ");
            ushort opCode = ushort.TryParse(Console.ReadLine(), out ushort oc) ? oc : (ushort)1;

            Console.Write("Enter Sequence Number (default: 0): ");
            ushort sequenceNumber = ushort.TryParse(Console.ReadLine(), out ushort sn) ? sn : (ushort)0;

            Console.Write("Enter Timestamp (default: 0): ");
            uint timestamp = uint.TryParse(Console.ReadLine(), out uint ts) ? ts : 0u;

            Console.Write("Enter Leopard Sequence Number (default: 0): ");
            uint leopardSequenceNumber = uint.TryParse(Console.ReadLine(), out uint lsn) ? lsn : 0u;

            // Build command
            byte[] result = CommandBuilder.BuildOpcodeCommand(pabPortSerialNumber, leopardSequence, opCode, sequenceNumber, timestamp, leopardSequenceNumber);

            Console.WriteLine("\n=== Generated Opcode Command ===");
            DisplayResult(result);
        }

        static void GenerateLeopardSequenceInteractive()
        {
            Console.WriteLine("\n=== Generate Leopard Sequence ===");
            Console.Write("Enter command (e.g., 'A' or 'AB'): ");
            string command = Console.ReadLine()?.Trim() ?? "";

            if (string.IsNullOrEmpty(command))
            {
                Console.WriteLine("No command entered. Using default: 'A'");
                command = "A";
            }

            char id = command.Length > 0 ? command[0] : 'A';
            char cmd = command.Length > 1 ? command[1] : id;

            byte[] leopardSequence = CommandBuilder.BuildCommand(id, cmd);

            Console.WriteLine("\n=== Generated Leopard Sequence ===");
            DisplayResult(leopardSequence);
        }

        static byte[] ParseHexString(string hex)
        {
            if (string.IsNullOrWhiteSpace(hex))
                return new byte[0];

            // Remove spaces and common separators
            hex = hex.Replace(" ", "").Replace("-", "").Replace("0x", "");

            // Ensure even length
            if (hex.Length % 2 != 0)
                hex = "0" + hex;

            try
            {
                return Enumerable.Range(0, hex.Length)
                    .Where(x => x % 2 == 0)
                    .Select(x => Convert.ToByte(hex.Substring(x, 2), 16))
                    .ToArray();
            }
            catch
            {
                return new byte[0];
            }
        }

        static void DisplayResult(byte[] data)
        {
            Console.WriteLine($"Length: {data.Length} bytes");
            Console.WriteLine($"Hex (with spaces): {BitConverter.ToString(data).Replace("-", " ")}");
            Console.WriteLine($"Hex (compact): {BitConverter.ToString(data).Replace("-", "")}");
            Console.WriteLine($"Byte array: [{string.Join(", ", data.Select(b => $"0x{b:X2}"))}]");
            Console.WriteLine($"Decimal values: [{string.Join(", ", data)}]");
        }
    }

    public static class CommandBuilder
    {
        public static byte[] BuildCommand(char ID, char command)
        {
            byte[] packet = [(byte)'0', (byte)ID, (byte)command];
            ushort crc = CalcCRC16(packet);
            byte[] crcBytes = BitConverter.GetBytes(crc);
            Array.Reverse(crcBytes);
            return [.. packet, .. crcBytes, 0x0D];
        }

        private static ushort CalcCRC16(byte[] data)
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
            byte[] command = [(byte)'S', (byte)'K', 0, 0, 0, 0, 0, 0,
                ..BitConverter.GetBytes(sequenceNumber),
                ..BitConverter.GetBytes(opCode),
                ..BitConverter.GetBytes(pabPortSerialNumber),
                ..BitConverter.GetBytes(timestamp),
                ..BitConverter.GetBytes(leopardSequenceNumber),
                ..leopardSequence];
            
            // Calculate length
            ushort length = (ushort)command.Length;
            command[2] = (byte)(length & 0xFF);
            command[3] = (byte)((length >> 8) & 0xFF);
            
            // Calculate checksum: all bytes except checksum (bytes 6–7)
            ushort checksum = CalculateChecksum(command);
            command[6] = (byte)(checksum & 0xFF);
            command[7] = (byte)((checksum >> 8) & 0xFF);

            return command;
        }

        private static ushort CalculateChecksum(byte[] data)
        {
            int sum = 0;
            for (int i = 0; i < data.Length; i++)
            {
                sum += data[i];
            }
            return (ushort)(~sum); // Logic NOT
        }
    }
}