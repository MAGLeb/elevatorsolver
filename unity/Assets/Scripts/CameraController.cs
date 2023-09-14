using UnityEngine;

public class CameraController : MonoBehaviour
{
    public float moveSpeed = 5f; // Скорость перемещения
    public float sensitivity = 2f; // Чувствительность камеры при вращении
    public float zoomSpeed = 5f; // Скорость приближения/отдаления

    private void Update()
    {
        float moveZ = Input.GetAxis("Horizontal"); // W/S для передвижения влево и вправо
        float moveX = Input.GetAxis("Vertical");   // A/D для приближения и отдаления

        Vector3 move = new Vector3(moveX, 0, -moveZ) * moveSpeed * Time.deltaTime;
        transform.Translate(move, Space.World);

        // Вращение камеры при удерживании правой кнопки мыши
        if (Input.GetMouseButton(1))
        {
            float mouseX = Input.GetAxis("Mouse X");
            float mouseY = Input.GetAxis("Mouse Y");

            Vector3 newRotation = transform.eulerAngles;
            newRotation.y += mouseX * sensitivity;
            newRotation.x -= mouseY * sensitivity;

            transform.eulerAngles = newRotation;
        }
        
        // Приближение/отдаление с помощью колесика мыши
        float zoom = Input.GetAxis("Mouse ScrollWheel");
        transform.Translate(0, 0, zoom * zoomSpeed, Space.Self);
    }
}
