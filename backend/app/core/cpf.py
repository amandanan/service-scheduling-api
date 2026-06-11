import re


def normalize_cpf(value: str) -> str:
    """Strip everything that is not a digit (removes the ./- mask)."""
    return re.sub(r"\D", "", value or "")


def is_valid_cpf(value: str) -> bool:
    """Validate a Brazilian CPF, including its two check digits."""
    cpf = normalize_cpf(value)

    if len(cpf) != 11:
        return False

    # sequences of the same digit (000..., 111...) pass the checksum
    # but are not valid CPFs
    if cpf == cpf[0] * 11:
        return False

    for length in (9, 10):
        total = sum(
            int(cpf[i]) * (length + 1 - i)
            for i in range(length)
        )

        check_digit = (total * 10) % 11

        if check_digit == 10:
            check_digit = 0

        if check_digit != int(cpf[length]):
            return False

    return True


def validate_and_normalize_cpf(value: str) -> str:
    """Validate a CPF and return it normalized to 11 digits, or raise."""
    digits = normalize_cpf(value)

    if not is_valid_cpf(digits):
        raise ValueError("CPF inválido")

    return digits
