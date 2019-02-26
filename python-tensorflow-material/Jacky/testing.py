import numpy as np
labels = np.array([[1,1,1,0],
                    [1,1,1,0],
                    [1,1,1,0],
                    [1,1,1,0]], dtype=np.uint8)
predictions = np.array([[1,0,0,0],
                        [1,1,0,0],
                        [1,1,1,0],
                        [0,1,1,1]], dtype=np.uint8)
n_batches = len(labels)

print(n_batches)

n_items = labels.size
print(n_items)
accuracy = (labels == predictions).sum() / n_items
print("Accuracy : ", accuracy)


