using UnityEngine;

public class GameController : MonoBehaviour
{
    public int numberOfFloors = 5;
    public Floor[] floors;
    public ElevatorController elevatorController;

    void Awake()
    {
        CreateFloors();
    }

    void CreateFloors()
    {
        floors = new Floor[numberOfFloors];
        Vector3 startingPosition = this.transform.position;

        for (int i = 0; i < numberOfFloors; i++)
        {
            GameObject newFloorObject = GameObject.CreatePrimitive(PrimitiveType.Cube);
            newFloorObject.name = "Floor " + (i + 1);
            newFloorObject.transform.parent = this.transform;
            newFloorObject.transform.position = startingPosition + new Vector3(0, i + (i * 0.1f), 0);

            Floor floor = newFloorObject.AddComponent<Floor>();
            floor.Initialize(i, newFloorObject.transform, newFloorObject.GetComponent<MeshRenderer>());
            
            floors[i] = floor;
        }
    }
}