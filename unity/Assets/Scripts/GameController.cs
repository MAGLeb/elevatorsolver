using UnityEngine;

public class GameController : MonoBehaviour
{
    public int numberOfFloors = 10;
    public Floor[] floors;
    public ElevatorController elevatorController;

    void Awake()
    {
        CreateFloors();
		elevatorController.Floors = floors;
    }

    void CreateFloors()
    {
        floors = new Floor[numberOfFloors];
        Vector3 startingPosition = this.transform.position;

        for (int i = 0; i < numberOfFloors; i++)
        {
            GameObject newFloorObject = GameObject.CreatePrimitive(PrimitiveType.Cube);
            newFloorObject.name = "Floor " + (i);
            newFloorObject.transform.parent = this.transform;
            newFloorObject.transform.position = startingPosition + new Vector3(0, i + (i * 0.1f), 0);

            Floor floor = newFloorObject.AddComponent<Floor>();
            floor.Initialize(i, newFloorObject.transform, newFloorObject.GetComponent<MeshRenderer>());
            
            floors[i] = floor;

        	// Создаем 3D текст и присваиваем его этажу
   			GameObject textObj = new GameObject("FloorNumberText");
    		textObj.transform.parent = newFloorObject.transform;
			float zShift = i + 1 >= 10 ? 0.3f : 0.15f;
    		textObj.transform.localPosition = new Vector3(-0.6f, 0.4f, zShift); 
    		textObj.transform.localEulerAngles = new Vector3(0, 90, 0); 
			textObj.transform.localScale = new Vector3(0.5f, 0.5f, 0.5f); 

    		TextMesh textMesh = textObj.AddComponent<TextMesh>();
    		textMesh.text = (i + 1).ToString();
    		textMesh.fontSize = 12;
    		textMesh.color = Color.black;

    		floor.textMesh = textMesh;
        }
    }
}