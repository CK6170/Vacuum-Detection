using System;
using System.Globalization;
using System.Text;

namespace LeopardCommandTool
{
	public static class HexUtils
	{
		public static bool TryParseHexBytes(string? input, out byte[]? bytes, out string? error)
		{
			bytes = null;
			error = null;
			if (string.IsNullOrWhiteSpace(input))
			{
				bytes = Array.Empty<byte>();
				return true;
			}
			try
			{
				string compact = input.Replace(" ", string.Empty)
					.Replace("-", string.Empty)
					.Replace(",", string.Empty)
					.Replace("0x", string.Empty, true, CultureInfo.InvariantCulture);
				if (compact.Length % 2 != 0)
				{
					compact = "0" + compact;
				}
				int length = compact.Length / 2;
				byte[] result = new byte[length];
				for (int i = 0; i < length; i++)
				{
					result[i] = byte.Parse(compact.Substring(i * 2, 2), NumberStyles.HexNumber, CultureInfo.InvariantCulture);
				}
				bytes = result;
				return true;
			}
			catch (Exception ex)
			{
				error = ex.Message;
				return false;
			}
		}

		public static string BytesToHex(byte[] bytes)
		{
			if (bytes.Length == 0) return string.Empty;
			StringBuilder sb = new StringBuilder(bytes.Length * 3);
			for (int i = 0; i < bytes.Length; i++)
			{
				if (i > 0) sb.Append(' ');
				sb.Append(bytes[i].ToString("X2", CultureInfo.InvariantCulture));
			}
			return sb.ToString();
		}

		public static bool TryParseUInt16(string? input, out ushort value, out string? error)
		{
			value = 0;
			error = null;
			if (string.IsNullOrWhiteSpace(input)) { error = "empty"; return false; }
			try
			{
				if (IsHex(input))
				{
					string s = NormalizeHex(input);
					value = ushort.Parse(s, NumberStyles.HexNumber, CultureInfo.InvariantCulture);
				}
				else
				{
					value = ushort.Parse(input, NumberStyles.Integer, CultureInfo.InvariantCulture);
				}
				return true;
			}
			catch (Exception ex)
			{
				error = ex.Message;
				return false;
			}
		}

		public static bool TryParseUInt32(string? input, out uint value, out string? error)
		{
			value = 0;
			error = null;
			if (string.IsNullOrWhiteSpace(input)) { error = "empty"; return false; }
			try
			{
				if (IsHex(input))
				{
					string s = NormalizeHex(input);
					value = uint.Parse(s, NumberStyles.HexNumber, CultureInfo.InvariantCulture);
				}
				else
				{
					value = uint.Parse(input, NumberStyles.Integer, CultureInfo.InvariantCulture);
				}
				return true;
			}
			catch (Exception ex)
			{
				error = ex.Message;
				return false;
			}
		}

		public static bool TryParseCharOrByte(string? input, out byte value, out string? error)
		{
			value = 0;
			error = null;
			if (string.IsNullOrEmpty(input)) { error = "empty"; return false; }
			input = input.Trim();
			try
			{
				if (input.Length == 1 && !char.IsWhiteSpace(input[0]))
				{
					value = (byte)input[0];
					return true;
				}
				if (IsHex(input))
				{
					string s = NormalizeHex(input);
					value = byte.Parse(s, NumberStyles.HexNumber, CultureInfo.InvariantCulture);
					return true;
				}
				value = byte.Parse(input, NumberStyles.Integer, CultureInfo.InvariantCulture);
				return true;
			}
			catch (Exception ex)
			{
				error = ex.Message;
				return false;
			}
		}

		private static bool IsHex(string s)
		{
			s = s.Trim();
			return s.StartsWith("0x", StringComparison.OrdinalIgnoreCase) || ContainsHexLetters(s);
		}

		private static bool ContainsHexLetters(string s)
		{
			for (int i = 0; i < s.Length; i++)
			{
				char c = s[i];
				if ((c >= 'A' && c <= 'F') || (c >= 'a' && c <= 'f')) return true;
			}
			return false;
		}

		private static string NormalizeHex(string s)
		{
			s = s.Trim();
			if (s.StartsWith("0x", StringComparison.OrdinalIgnoreCase)) s = s.Substring(2);
			return s.Replace(" ", string.Empty).Replace("_", string.Empty);
		}
	}
}

