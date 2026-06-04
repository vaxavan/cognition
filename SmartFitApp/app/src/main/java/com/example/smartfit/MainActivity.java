package com.example.smartfit;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        View[] views = {
            findViewById(R.id.textWelcome),
            findViewById(R.id.textBrand),
            findViewById(R.id.dividerLine),
            findViewById(R.id.textSubtitle),
            findViewById(R.id.btnGoToLogin),
            findViewById(R.id.btnGoToReg)
        };

        for (int i = 0; i < views.length; i++) {
            views[i].setTranslationY(40f);
            views[i].animate()
                .alpha(1f)
                .translationY(0f)
                .setDuration(700)
                .setStartDelay(200 + i * 130)
                .start();
        }

        findViewById(R.id.btnGoToLogin).setOnClickListener(v ->
            startActivity(new Intent(this, LoginActivity.class)));

        findViewById(R.id.btnGoToReg).setOnClickListener(v ->
            startActivity(new Intent(this, RegisterActivity.class)));
    }
}
