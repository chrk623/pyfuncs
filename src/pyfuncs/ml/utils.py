from sklearn import model_selection


def create_folds(df, n_splits, random_state=42, save=True, out_path="./folds.csv"):
    df = df.copy()
    df["kfold"] = -1
    kf = model_selection.KFold(n_splits=n_splits, random_state=random_state, shuffle=True)

    for fold, (train_index, validation_index) in enumerate(kf.split(X=df)):
        df.loc[validation_index, "kfold"] = fold

    print(df.kfold.value_counts())

    if save:
        df.to_csv(out_path, index=False)

    return df