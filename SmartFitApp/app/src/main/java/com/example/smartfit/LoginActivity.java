package com.example.smartfit;

import android.content.Intent;
import android.os.Bundle;
import android.text.TextUtils;
import android.widget.EditText;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class LoginActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        DatabaseHelper db = new DatabaseHelper(this);
        EditText etUser = findViewById(R.id.etUser);
        EditText etPass = findViewById(R.id.etPass);
        TextView tvError = findViewById(R.id.tvLoginError);

        findViewById(R.id.btnBackLogin).setOnClickListener(v -> finish());

        findViewById(R.id.btnLogin).setOnClickListener(v -> {
            String user = etUser.getText().toString().trim();
            String pass = etPass.getText().toString();

            tvError.setVisibility(android.view.View.GONE);

            if (TextUtils.isEmpty(user)) {
                tvError.setText("Введите логин");
                tvError.setVisibility(android.view.View.VISIBLE);
                return;
            }
            if (TextUtils.isEmpty(pass)) {
                tvError.setText("Введите пароль");
                tvError.setVisibility(android.view.View.VISIBLE);
                return;
            }

            if (db.checkLogin(user, pass)) {
                Intent intent = new Intent(this, HomeActivity.class);
                intent.putExtra("USER_NAME", user);
                startActivity(intent);
                finish();
            } else {
                tvError.setText("Неверный логин или пароль");
                tvError.setVisibility(android.view.View.VISIBLE);
            }
        });
    }
}
