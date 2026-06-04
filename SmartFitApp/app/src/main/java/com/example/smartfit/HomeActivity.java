package com.example.smartfit;

import android.content.Intent;
import android.os.Bundle;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class HomeActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home);

        String user = getIntent().getStringExtra("USER_NAME");
        String displayName = (user != null && !user.isEmpty()) ? user : "Атлет";
        ((TextView) findViewById(R.id.tvHello)).setText(displayName);

        findViewById(R.id.btnProfile).setOnClickListener(v -> {
            Intent intent = new Intent(this, ProfileActivity.class);
            intent.putExtra("USER_NAME", user);
            startActivity(intent);
        });

        findViewById(R.id.btnWorkouts).setOnClickListener(v -> {
            Intent intent = new Intent(this, TrainingHistoryActivity.class);
            intent.putExtra("USER_NAME", user);
            startActivity(intent);
        });
    }
}
