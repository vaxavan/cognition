package com.example.smartfit;

import android.content.Intent;
import android.database.Cursor;
import android.os.Bundle;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;

public class TrainingHistoryActivity extends AppCompatActivity {
    private DatabaseHelper db;
    private String currentUser;
    private LinearLayout container;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_training_history);

        db = new DatabaseHelper(this);
        currentUser = getIntent().getStringExtra("USER_NAME");

        container = findViewById(R.id.historyContainer);
        Button btnNew = findViewById(R.id.btnNewTraining);

        findViewById(R.id.btnBackHistory).setOnClickListener(v -> finish());

        loadHistory();

        btnNew.setOnClickListener(v -> {
            long workoutId = db.createWorkout(currentUser);
            Intent intent = new Intent(this, ExerciseListActivity.class);
            intent.putExtra("WORKOUT_ID", workoutId);
            intent.putExtra("USER_NAME", currentUser);
            startActivity(intent);
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        loadHistory();
    }

    private void loadHistory() {
        container.removeAllViews();
        Cursor cursor = db.getWorkouts(currentUser);
        if (cursor.getCount() == 0) {
            TextView empty = new TextView(this);
            empty.setText("Нет завершённых тренировок");
            empty.setTextColor(ContextCompat.getColor(this, R.color.text_secondary));
            empty.setTextSize(15);
            empty.setPadding(0, 32, 0, 0);
            container.addView(empty);
            cursor.close();
            return;
        }
        while (cursor.moveToNext()) {
            long id = cursor.getLong(0);
            String date = cursor.getString(2);
            int exCount = db.getExerciseCount(id);
            int totalReps = db.getTotalReps(id);

            LinearLayout item = (LinearLayout) getLayoutInflater().inflate(R.layout.item_workout, null);
            TextView tvDate = item.findViewById(R.id.tvWorkoutDate);
            TextView tvSummary = item.findViewById(R.id.tvWorkoutSummary);
            tvDate.setText(date);
            tvSummary.setText(exCount + " упражнений · " + totalReps + " повторений");

            item.setOnClickListener(v ->
                Toast.makeText(TrainingHistoryActivity.this,
                    date + "\n" + exCount + " упр., " + totalReps + " повт.",
                    Toast.LENGTH_SHORT).show());
            container.addView(item);
        }
        cursor.close();
    }
}
