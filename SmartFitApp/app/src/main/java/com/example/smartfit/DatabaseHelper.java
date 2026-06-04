package com.example.smartfit;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class DatabaseHelper extends SQLiteOpenHelper {
    public DatabaseHelper(Context context) {
        super(context, "UserDB", null, 2);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE IF NOT EXISTS users(user TEXT PRIMARY KEY, pass TEXT)");
        db.execSQL("CREATE TABLE IF NOT EXISTS workouts(" +
                "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
                "user TEXT, start_date TEXT, status TEXT)");
        db.execSQL("CREATE TABLE IF NOT EXISTS sets(" +
                "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
                "workout_id INTEGER, exercise TEXT, reps INTEGER, " +
                "FOREIGN KEY(workout_id) REFERENCES workouts(id))");
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        if (oldVersion < 2) {
            db.execSQL("CREATE TABLE IF NOT EXISTS workouts(" +
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
                    "user TEXT, start_date TEXT, status TEXT)");
            db.execSQL("CREATE TABLE IF NOT EXISTS sets(" +
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
                    "workout_id INTEGER, exercise TEXT, reps INTEGER, " +
                    "FOREIGN KEY(workout_id) REFERENCES workouts(id))");
        }
    }

    public boolean register(String u, String p) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put("user", u);
        cv.put("pass", p);
        long result = db.insert("users", null, cv);
        return result != -1;
    }

    public boolean checkLogin(String u, String p) {
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor c = db.rawQuery("SELECT * FROM users WHERE user=? AND pass=?", new String[]{u, p});
        boolean exists = c.getCount() > 0;
        c.close();
        return exists;
    }

    public long createWorkout(String user) {
        SQLiteDatabase db = getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put("user", user);
        SimpleDateFormat sdf = new SimpleDateFormat("dd.MM.yyyy HH:mm", Locale.getDefault());
        cv.put("start_date", sdf.format(new Date()));
        cv.put("status", "active");
        return db.insert("workouts", null, cv);
    }

    public void finishWorkout(long workoutId) {
        SQLiteDatabase db = getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put("status", "completed");
        db.update("workouts", cv, "id=?", new String[]{String.valueOf(workoutId)});
    }

    public Cursor getWorkouts(String user) {
        SQLiteDatabase db = getReadableDatabase();
        return db.rawQuery(
                "SELECT * FROM workouts WHERE user=? AND status='completed' ORDER BY id DESC",
                new String[]{user});
    }

    public void saveSet(long workoutId, String exercise, int reps) {
        SQLiteDatabase db = getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put("workout_id", workoutId);
        cv.put("exercise", exercise);
        cv.put("reps", reps);
        db.insert("sets", null, cv);
    }

    public Cursor getSets(long workoutId) {
        SQLiteDatabase db = getReadableDatabase();
        return db.rawQuery("SELECT * FROM sets WHERE workout_id=? ORDER BY id",
                new String[]{String.valueOf(workoutId)});
    }

    public int getExerciseCount(long workoutId) {
        SQLiteDatabase db = getReadableDatabase();
        Cursor c = db.rawQuery(
                "SELECT COUNT(DISTINCT exercise) FROM sets WHERE workout_id=?",
                new String[]{String.valueOf(workoutId)});
        int count = 0;
        if (c.moveToFirst()) count = c.getInt(0);
        c.close();
        return count;
    }

    public int getTotalReps(long workoutId) {
        SQLiteDatabase db = getReadableDatabase();
        Cursor c = db.rawQuery(
                "SELECT COALESCE(SUM(reps), 0) FROM sets WHERE workout_id=?",
                new String[]{String.valueOf(workoutId)});
        int total = 0;
        if (c.moveToFirst()) total = c.getInt(0);
        c.close();
        return total;
    }
}
