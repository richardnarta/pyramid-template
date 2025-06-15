import pytest
from marshmallow import ValidationError
from setara_backend.schemas import UserSchema


@pytest.fixture
def base_payload():
    """Provides a valid base dictionary for schema loading."""
    return {
        "login_method": "phone",
        "user_identifier": "+6281234567890",
        "user_password": "ValidPassword1!",
        "user_notification_token": "a-valid-fcm-token-string"
    }


class TestUserSchema:
    @pytest.mark.parametrize("method, identifier", [
        ("phone", "+6281234567890"),
        ("email", "test.user@example.com"),
        ("username", "testuser123")
    ])
    def test_valid_payloads_succeed(self, base_payload, method, identifier):
        """Tests that the schema loads successfully with valid data for each login method."""
        # Setup
        payload = base_payload.copy()
        payload["login_method"] = method
        payload["user_identifier"] = identifier

        schema = UserSchema()

        # Action
        loaded_data = schema.load(payload)

        # Assert
        assert loaded_data["login_method"] == method
        assert loaded_data["user_identifier"] == identifier

    @pytest.mark.parametrize("missing_field", [
        "login_method",
        "user_password",
        "user_notification_token"
    ])
    def test_missing_required_fields_fail(self, base_payload, missing_field):
        """Tests that a missing required field raises a ValidationError."""
        # Setup
        del base_payload[missing_field]
        schema = UserSchema()

        # Action
        with pytest.raises(ValidationError) as e:
            schema.load(base_payload)

        # Assert
        assert missing_field in e.value.messages

    def test_invalid_login_method_fails(self, base_payload):
        """Tests that an unsupported login_method fails validation."""
        # Setup
        base_payload["login_method"] = "facebook"
        schema = UserSchema()

        # Action
        with pytest.raises(ValidationError) as e:
            schema.load(base_payload)

        # Assert
        assert "login_method" in e.value.messages
        assert "must be one of" in e.value.messages["login_method"][0]

    @pytest.mark.parametrize("password, reason", [
        ("short", "is too short"),
        ("NoSpecialChar1", "is missing a special character"),
        ("nouppercase1!", "is missing an uppercase letter"),
        ("NoDigitChar!", "is missing a digit")
    ])
    def test_invalid_password_formats_fail(self, base_payload, password, reason):
        """Tests various invalid password formats against the regex."""
        # Setup
        base_payload["user_password"] = password
        schema = UserSchema()

        # Action
        with pytest.raises(ValidationError) as e:
            schema.load(base_payload)

        # Assert
        assert "user_password" in e.value.messages
        assert "Password harus berjumlah minimal 8 karakter dan memiliki sebuah huruf besar, sebuah angka, dan sebuah simbol." in e.value.messages[
            "user_password"][0]

    @pytest.mark.parametrize("invalid_phone, reason", [
        ("081234567890", "doesn't start with +62"),
        ("+6212345", "is too short"),
        ("+628123456789012345", "is too long"),
        ("not-a-phone-number", "contains invalid characters")
    ])
    def test_phone_identifier_validation(self, base_payload, invalid_phone, reason):
        """Tests that invalid phone numbers fail when login_method is 'phone'."""
        # Setup
        base_payload["login_method"] = "phone"
        base_payload["user_identifier"] = invalid_phone
        schema = UserSchema()

        # Action
        with pytest.raises(ValidationError) as e:
            schema.load(base_payload)

        # Assert
        assert "user_identifier" in e.value.messages
        assert "Format nomor telepon tidak valid." in e.value.messages["user_identifier"][0]

    def test_email_identifier_validation(self, base_payload):
        """Tests that an invalid email fails when login_method is 'email'."""
        # Setup
        base_payload["login_method"] = "email"
        base_payload["user_identifier"] = "not-a-valid-email"
        schema = UserSchema()

        # Action
        with pytest.raises(ValidationError) as e:
            schema.load(base_payload)

        # Assert
        assert "user_identifier" in e.value.messages
        assert "Email tidak valid." in e.value.messages["user_identifier"][0]

    def test_username_identifier_validation(self, base_payload):
        """Tests that a short username fails when login_method is 'username'."""
        # Setup
        base_payload["login_method"] = "username"
        base_payload["user_identifier"] = "ab"  # less than 3 chars
        schema = UserSchema()

        # Action
        with pytest.raises(ValidationError) as e:
            schema.load(base_payload)

        # Assert
        assert "user_identifier" in e.value.messages
        assert "at least 3 characters long" in e.value.messages["user_identifier"][0]
