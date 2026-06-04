package com.example.smartfit;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

public class ExerciseListActivity extends AppCompatActivity {
    private long workoutId;
    private DatabaseHelper db;
    private String currentUser;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_exercise_list);

        db = new DatabaseHelper(this);
        workoutId = getIntent().getLongExtra("WORKOUT_ID", -1);
        currentUser = getIntent().getStringExtra("USER_NAME");

        findViewById(R.id.btnBackExList).setOnClickListener(v -> {
            db.finishWorkout(workoutId);
            finish();
        });

        View[] items = {
            findViewById(R.id.tvWorkoutTitle),
            findViewById(R.id.cardSquats),
            findViewById(R.id.cardShoulders),
            findViewById(R.id.cardBiceps)
        };

        for (int i = 0; i < items.length; i++) {
            if (items[i] != null) {
                items[i].setTranslationX(-80f);
                items[i].animate()
                    .alpha(1f)
                    .translationX(0f)
                    .setDuration(500)
                    .setStartDelay(150 + i * 120)
                    .start();
            }
        }

        findViewById(R.id.cardSquats).setOnClickListener(v -> startExercise("squat"));
        findViewById(R.id.cardShoulders).setOnClickListener(v -> startExercise("shoulders"));
        findViewById(R.id.cardBiceps).setOnClickListener(v -> startExercise("biceps"));

        findViewById(R.id.btnFinishWorkout).setOnClickListener(v -> {
            db.finishWorkout(workoutId);
            Toast.makeText(this, "Тренировка завершена!", Toast.LENGTH_SHORT).show();
            finish();
        });
    }

    private void startExercise(String exercise) {
        Intent intent = new Intent(this, ExerciseActivity.class);
        intent.putExtra("WORKOUT_ID", workoutId);
        intent.putExtra("EXERCISE_TYPE", exercise);
        intent.putExtra("USER_NAME", currentUser);
        startActivity(intent);
    }
}
