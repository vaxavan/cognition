package com.example.smartfit;

import android.os.Bundle;
import android.text.TextUtils;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

public class RegisterActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register);

        DatabaseHelper db = new DatabaseHelper(this);
        EditText etUser = findViewById(R.id.etUserReg);
        EditText etPass = findViewById(R.id.etPassReg);
        TextView tvError = findViewById(R.id.tvRegError);

        findViewById(R.id.btnBackRegister).setOnClickListener(v -> finish());

        findViewById(R.id.btnRegister).setOnClickListener(v -> {
            String user = etUser.getText().toString().trim();
            String pass = etPass.getText().toString();

            tvError.setVisibility(android.view.View.GONE);

            if (TextUtils.isEmpty(user)) {
                tvError.setText("Придумайте логин");
                tvError.setVisibility(android.view.View.VISIBLE);
                return;
            }
            if (user.length() < 3) {
                tvError.setText("Логин должен быть не короче 3 символов");
                tvError.setVisibility(android.view.View.VISIBLE);
                return;
            }
            if (TextUtils.isEmpty(pass)) {
                tvError.setText("Придумайте пароль");
                tvError.setVisibility(android.view.View.VISIBLE);
                return;
            }
            if (pass.length() < 4) {
                tvError.setText("Пароль должен быть не короче 4 символов");
                tvError.setVisibility(android.view.View.VISIBLE);
                return;
            }

            if (db.register(user, pass)) {
                Toast.makeText(this, "Аккаунт создан! Теперь войдите.", Toast.LENGTH_SHORT).show();
                finish();
            } else {
                tvError.setText("Этот логин уже занят");
                tvError.setVisibility(android.view.View.VISIBLE);
            }
        });
    }
}
